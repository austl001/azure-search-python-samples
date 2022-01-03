
import os
import pdfplumber
import pandas as pd
import numpy as np

# Get list of names of pdf files 
pdf_dir = os.getcwd() + "/bulk-upload/upload-documents/"
pdf_list = os.listdir(pdf_dir)
print(pdf_list)

# Extract first page of text and remove empty lines to get just the pdf title on its own

pdf = pdfplumber.open(pdf_dir + pdf_list[44])
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

" ".join(by_size(text, 3)[0:3])

pdf_titles = []
for i in range(0, len(pdf_list)):
    pdf = pdfplumber.open(pdf_dir + pdf_list[i])
    page = pdf.pages[0]
    text = page.extract_text().split("\n")
    title = " ".join(by_size(text, 3)[0:3])
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

df = pd.DataFrame(
    {
    "pdfFileName" : pdf_list,
    "pdfTitle" : pdf_titles,
    "pdfType": type_list
    }
)

print(df)