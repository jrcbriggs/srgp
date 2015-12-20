'''
Created on 18 Dec 2015

@author: julian

Append the nationbuilder_id to a registre csv
'''

from csv import DictReader, DictWriter, reader, writer
import os.path

base = '/home/julian/SRGP/register/2015_16/record_linking'
register = os.path.join(base, 'PUB_AREA_W_CENTRA_01-12-2015NB.csv')
register_updated = register.replace('.csv', '_updated.csv')
sf_old2new_nb = os.path.join(base, 'sf_old2new_nb.csv')
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


def read_csv(fin):
    with open(fin, 'r') as fhin:
        dr = DictReader(fhin)
        rows = list(dr)
        fieldnames = dr.fieldnames
        return (fieldnames, rows)


def write_csv(fout, fieldnames, rows):
    '''Write a list of dict to a csv file using fieldnames
    '''
    with open(fout, 'w') as fhout:
        dw = DictWriter(fhout, fieldnames)
        dw.writeheader()
        dw.writerows(rows)


if __name__ == '__main__':
    # Read register
    (fieldnames, rows) = read_csv(register)


    # Create sf_new to nb_id lookup
    (unused, lookup) = read_csv(sf_old2new_nb)
    sf_new2nb = {row.get(k2): row.get(k3) for row in lookup}
    print(sf_new2nb)

    # Append nb_id to register
    for row in rows:
        sf_new = row.get(k0)
        row[k3] = sf_new2nb.get(sf_new)

    # Write out
    fieldnames.append(k3)
    write_csv(register_updated, fieldnames, rows)

