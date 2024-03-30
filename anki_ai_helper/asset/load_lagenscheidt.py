import zipfile
import os

apkg_file = './langenscheidt-2000.apkg'
extract_folder = '/tmp/langenscheidt'

with zipfile.ZipFile(apkg_file, 'r') as zip_ref:
    zip_ref.extractall(extract_folder)

collection_file = os.path.join(extract_folder, 'collection.anki2')

from ankipandas import Collection

col = Collection(collection_file)  # Use the path to your extracted collection.anki2 file

# Now you can interact with your collection
# For example, to get all notes:
notes = col.notes

print(notes.head())  # Displays the first few rows of your notes DataFrame

notes['nflds'].iloc[0]
