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

base = '/home/julian/SRGP/register/2015_16/record_linking'
nb_export = os.path.join(base, 'nationbuilderExportCentralWard.csv')
registers_linked = os.path.join(base, 'CentralWardRegistersLinked2015-12-01.csv')
registers_linked_fixed = registers_linked.replace('.csv', 'fixed.csv')
sf_old2new_nb = os.path.join(base, 'sf_old2new_nb.csv')
fout = os.path.join(base, 'statefile_id2nationabuilder_id.csv')
k0 = 'state_file_id'
k1 = 'state_file_id_old'
k2 = 'state_file_id_new'
k3 = 'nationbuilder_id'


def select_columns(fin, col_names):
    '''From a csv file, create a list of dict [{...}, ...]
    using the given column names
    '''
    with open(fin, 'r') as fhin:
        return [{k: row[k] for k in col_names} for row in DictReader(fhin)]


def fix_header(fin, fout):
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


def write_csv(fout, headers, rows):
    '''Write a list of dict to a csv file using headers
    '''
    with open(fout, 'w') as fhout:
        dw = DictWriter(fhout, headers)
        dw.writeheader()
        dw.writerows(rows)


def create_nb_sf_old_new(registers_linked, k1, k2, k3, sf_old2nb):
    '''Create a table ([{...,}, ...], eg
    sf_old, sf_new, nb_id
    '''
    nb_sf_old_new = select_columns(registers_linked, (k1, k2))
    for row in nb_sf_old_new:
        sf_old = row[k1]
        nb_id = sf_old2nb.get(sf_old)
        row[k3] = nb_id
    return nb_sf_old_new


if __name__ == '__main__':
    # Create_a dict {sf_old: nb_id}
    sf_old2nb = {r[k0]: r[k3] for r in select_columns(nb_export, (k0, k3,))}

    # Disambiguate duplicate state_file_id columns in registerLinked file
    fix_header(registers_linked, registers_linked_fixed)

    # Create a lookup table [nb_id, sf_old, sf_new]
    nb_sf_old_new = create_nb_sf_old_new(registers_linked_fixed, k1, k2, k3, sf_old2nb)

    # Write table: sf_old, sf_new, nb_id
    write_csv(sf_old2new_nb, [k1, k2, k3], nb_sf_old_new)
