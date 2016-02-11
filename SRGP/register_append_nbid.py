'''
Created on 18 Dec 2015

@author: julian

Create table sf_old2new_nb: sf_old, sf_new, nb_id
where sf is state_file
Reads:
  NB Export as csv
  RegistersLinked csv
'''

from csv import DictReader, DictWriter, reader, writer
from os.path import expanduser
import os.path


class CsvHandler:

    def csv_read(self, fin):
        '''Read CSV file
        '''
        with open(fin, 'r') as fhin:
            dr = DictReader(fhin)
            rows = list(dr)
            fieldnames = dr.fieldnames
            return (fieldnames, rows)

    def csv_write(self, fout, headers, rows):
        '''Write a list of dict to a csv file using headers
        '''
        with open(fout, 'w') as fhout:
            dw = DictWriter(fhout, headers)
            dw.writeheader()
            dw.writerows(rows)

    def select_columns(self, fin, col_names):
        '''From a csv file, create a list of dict [{...}, ...]
        using the given column names
        '''
        (unused, rows) = self.csv_read(fin)
        return [{k: row[k] for k in col_names} for row in rows]


class SfidsNbidCreator:

    sfid = 'state_file_id'
    sfid_old = 'state_file_id_old'
    sfid_new = 'state_file_id_new'
    nbid = 'nationbuilder_id'

    def __init__(self, csv_handler, base, nb_export, registers_linked):
        self.csv_handler = csv_handler
        self.nb_export = os.path.join(base, nb_export)
        self.registers_linked = os.path.join(base, registers_linked)
        self.registers_linked_fixed = registers_linked.replace('.csv', 'fixed.csv')


    def fix_header(self, fin, fout):
        '''Disambiguate 2 identical header labels, eg state_file_id
        return updated header, eg [ ..., state_file_id_old, ...state_file_id_new,...]
        '''
        with open(fin, 'r') as fhin:
            rows = list(reader(fhin, delimiter=','))
            header = rows[0]
            first = True
            for i in range(len(header)):
                if header[i] == 'state_file_id':
                    if first:
                        first = False
                        header[i] += '_old'
                    else:
                        header[i] += '_new'
        with open(fout, 'w') as fhout:
            writer(fhout).writerows(rows)

    def sfids_nbid_create_table(self, registers_linked, sf_old2nb):
        '''Create a table ([{...,}, ...], eg
        sf_old, sf_new, nb_id
        '''
        nb_sf_old_new = self.csv_handler.select_columns(registers_linked, (self.sfid_old, self.sfid_new))
        for row in nb_sf_old_new:
            sfid_old = row[self.sfid_old]
            sfid_old_unpadded = sfid_old[:2] + str(int(sfid_old[2:]))
            row[self.nbid] = sf_old2nb.get(sfid_old_unpadded)
        return nb_sf_old_new

    def sfids_nbid_create(self):
        # Create_a dict {sf_old: nb_id}
        sf_old2nb = {r[self.sfid]: r[self.nbid] for r in
                     self.csv_handler.select_columns(self.nb_export, (self.sfid, self.nbid,))}

        # Disambiguate duplicate state_file_id columns in registerLinked file
        self.fix_header(self.registers_linked, self.registers_linked_fixed)

        # Create a lookup table [nb_id, sf_old, sf_new]
        self.sfids_nbid = self.sfids_nbid_create_table(self.registers_linked_fixed, sf_old2nb)

    def sfids_nbid_write(self, filename):
        # Write table: sf_old, sf_new, nb_id
        pathname = os.path.join(base, filename)
        print('writing:', pathname)
        self.csv_handler.csv_write(pathname, [self.sfid_old, self.sfid_new, self.nbid], self.sfids_nbid)

    def zero_pad(self,):
        pass

class RegisterAppendNbId:

    sfid = 'state_file_id'
    sfid_old = 'state_file_id_old'
    sfid_new = 'state_file_id_new'
    nbid = 'nationbuilder_id'
    extern_id = 'extern_id'

    def __init__(self, csv_handler, base, register, sfids_nbid):
        self.csv_handler = csv_handler
        self.register = os.path.join(base, register)
        self.register_updated = self.register.replace('.csv', '_updated.csv')
        self.sfids_nbid = sfids_nbid

    def register_append_nbid(self):
        # Read register
        (fieldnames, rows) = self.csv_handler.csv_read(self.register)

        # Create sf_new to nb_id lookup
        sf_new2nb = {row.get(self.sfid_new): row.get(self.nbid) for row in self.sfids_nbid}
        sf_new2sf_old = {row.get(self.sfid_new): row.get(self.sfid_old) for row in self.sfids_nbid}

        # Append nb_id to register
        for row in rows:
            sf_new = row.get(self.sfid)
            row[self.nbid] = sf_new2nb.get(sf_new)
            row[self.extern_id] = sf_new2sf_old.get(sf_new)
        # Write out
        fieldnames.append(self.nbid)
        fieldnames.append(self.extern_id)
        print('writing:', self.register_updated)
        self.csv_handler.csv_write(self.register_updated, fieldnames, rows)


if __name__ == '__main__':
    base = expanduser('~/SRGP/register/2015_16/CentralConstituency')
    nb_export = 'nationbuilder-people-export-351-2016-01-06.csv'
    register_new = 'TtwAndDevWardRegisters2015-12-01NB.csv'
    registers_linked = 'CentralConstituencyWardRegistersLinked2015-12-01.csv'
    sfids_nbid = 'sfids_nbid.csv'

    csv_handler = CsvHandler()

    # Create Lookups
    imc = SfidsNbidCreator(csv_handler, base, nb_export, registers_linked)
    imc.sfids_nbid_create()
    imc.sfids_nbid_write(sfids_nbid)

    # Append NB id to new register
    RegisterAppendNbId(csv_handler, base, register_new, imc.sfids_nbid).register_append_nbid()
