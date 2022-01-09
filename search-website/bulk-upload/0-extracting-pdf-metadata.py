
import os
import pdfplumber
import pandas as pd
import numpy as np

# Prepare metadata for upload documents 1

# Get list of names of pdf files 
pdf_dir = os.getcwd() + "/bulk-upload/upload-documents-1/"
pdf_list = os.listdir(pdf_dir)
print(pdf_list)

# Extract first page of text and remove empty lines to get just the pdf title on its own

pdf = pdfplumber.open(pdf_dir + pdf_list[33])
page = pdf.pages[0]
text = page.extract_text().split("\n")
print(text[0:3])

for line in text:
    if len(line) > 1:
        print(line)

def by_size(text, length):
    result = []
    for line in text:
        if len(line) > length:
            result.append(line)
    return result

" ".join(by_size(text, 3)[0:6])

pdf_titles = []
for i in range(0, len(pdf_list)):
    pdf = pdfplumber.open(pdf_dir + pdf_list[i])
    page = pdf.pages[0]
    text = page.extract_text().split("\n")
    title = " ".join(by_size(text, 3)[0:6])
    pdf_titles.append(title)
print(pdf_titles)

# Define types of documents and extract based on title string

pdf_types_list = ["Code Subsidiary Document", "Operational Terms", "Operational Subsidiary Document", "Wholesale Contract", "Market Arrangements Code"]

type_list = []
for i in range(0, len(pdf_titles)):
    matched_types = []
    for type in pdf_types_list:
        matched_types.append(type in pdf_titles[i])
    type = np.extract(matched_types, pdf_types_list)[0]
    if len(type) > 1: 
        type_list.append(type) 
    else:
        type_list.append("Other")
print(type_list)

# Create data frame of attributes for attaching blob metadata

df1 = pd.DataFrame(
    {
    "FileName" : pdf_list,
    "DocumentTitle" : pdf_titles,
    "DocumentType" : type_list
    }
)

print(df1)

# Prepare metadata for upload documents 2

file_dir = os.getcwd() + "/bulk-upload/upload-documents-2/"
file_list = os.listdir(file_dir)

for file in file_list:
    print(file)

file_titles = []
file_types = []

for file in file_list:
    file_name, file_extension = os.path.splitext(file)
    file_titles.append(file_name)
    file_types.append(file_extension.split(".")[-1].lower())

df2 = pd.DataFrame(
    {
        "FileName" : file_list,
        "DocumentTitle" : file_titles,
        "DocumentType" : file_types
    }
)

print(df2)

# Combine metadata into one dataframe

df3 = pd.concat([df1, df2])

print(df3)

df3.to_pickle("bulk-upload/blob.metadata.pkl")