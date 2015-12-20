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
import os.path


class CsvHandler:

    def csv_read(self, fin):
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


class IdMapCreator:

    csv_handler = None
    registers_linked = None
    registers_linked_fixed = None
    registers_linked_fixed = None
    sf_old2new_nb = None
    fout = None
    sfid = 'state_file_id'
    sfid_old = 'state_file_id_old'
    sfid_new = 'state_file_id_new'
    nbid = 'nationbuilder_id'

    def __init__(self, csv_handler, base, nb_export, registers_linked, sfids_nbid):
        self.csv_handler = csv_handler
        self.nb_export = os.path.join(base, nb_export)
        self.registers_linked = os.path.join(base, registers_linked)
        self.registers_linked_fixed = registers_linked.replace('.csv', 'fixed.csv')
        self.sfids_nbid = os.path.join(base, sfids_nbid)
        self.fout = os.path.join(base, 'statefile_id2nationabuilder_id.csv')

    def select_columns(self, fin, col_names):
        '''From a csv file, create a list of dict [{...}, ...]
        using the given column names
        '''
        with open(fin, 'r') as fhin:
            return [{k: row[k] for k in col_names} for row in DictReader(fhin)]

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

    def create_nb_sf_old_new(self, registers_linked, sfid_old, sfid_new, nbid, sf_old2nb):
        '''Create a table ([{...,}, ...], eg
        sf_old, sf_new, nb_id
        '''
        nb_sf_old_new = self.select_columns(registers_linked, (sfid_old, sfid_new))
        for row in nb_sf_old_new:
            sf_old = row[sfid_old]
            nb_id = sf_old2nb.get(sf_old)
            row[nbid] = nb_id
        return nb_sf_old_new

    def id_map_create(self):
        # Create_a dict {sf_old: nb_id}
        sf_old2nb = {r[self.sfid]: r[self.nbid] for r in
                     self.select_columns(self.nb_export, (self.sfid, self.nbid,))}

        # Disambiguate duplicate state_file_id columns in registerLinked file
        self.fix_header(self.registers_linked, self.registers_linked_fixed)

        # Create a lookup table [nb_id, sf_old, sf_new]
        nb_sf_old_new = self.create_nb_sf_old_new(self.registers_linked_fixed, self.sfid_old,
                                                  self.sfid_new, self.nbid, sf_old2nb)

        # Write table: sf_old, sf_new, nb_id
        self.csv_handler.csv_write(self.sfids_nbid, [self.sfid_old, self.sfid_new, self.nbid],
                                   nb_sf_old_new)

class RegisterAppendNbId:

    sfid = 'state_file_id'
    sfid_old = 'state_file_id_old'
    sfid_new = 'state_file_id_new'
    nbid = 'nationbuilder_id'

    def __init__(self, csv_handler, base, register, sfids_nbid):
        self.csv_handler = csv_handler
        self.register = os.path.join(base, register)
        self.register_updated = self.register.replace('.csv', '_updated.csv')
        self.sfids_nbid = os.path.join(base, sfids_nbid)

    def select_columns(self, fin, col_names):
        '''From a csv file, create a list of dict [{...}, ...]
        using the given column names
        '''
        (unused, rows) = csv_read(fin)
        return [{k: row[k] for k in col_names} for row in rows]


    def register_append_nbid(self):
        # Read register
        (fieldnames, rows) = self.csv_handler.csv_read(self.register)

        # Create sf_new to nb_id lookup
        (unused, lookup) = self.csv_handler.csv_read(self.sfids_nbid)
        sf_new2nb = {row.get(self.sfid_new): row.get(self.nbid) for row in lookup}

        # Append nb_id to register
        for row in rows:
            sf_new = row.get(self.sfid)
            row[self.nbid] = sf_new2nb.get(sf_new)

        # Write out
        fieldnames.append(self.nbid)
        self.csv_handler.csv_write(self.register_updated, fieldnames, rows)


if __name__ == '__main__':
    csv_handler = CsvHandler()
    base = '/home/julian/SRGP/register/2015_16/record_linking'

    # Create Lookups
    nb_export = 'nationbuilderExportCentralWard.csv'
    registers_linked = 'CentralWardRegistersLinked2015-12-01.csv'
    sfids_nbid = 'sfids_nbid.csv'
    IdMapCreator(csv_handler, base, nb_export, registers_linked, sfids_nbid).id_map_create()

    # Append NB id to new register
    register = 'PUB_AREA_W_CENTRA_01-12-2015NB.csv'
    RegisterAppendNbId(csv_handler, base, register, sfids_nbid).register_append_nbid()

