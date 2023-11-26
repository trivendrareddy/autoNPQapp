import pandas as pd
import numpy as np
from datetime import datetime
import time
import streamlit as st

def allocate_delivery_quantities(merged_df, roundoff, march, deliverylots):
    if roundoff != 0:
        rounded_column_name = f'NPQ rounded off to {roundoff}'
        merged_df[rounded_column_name] = round(merged_df['NPQ'] / roundoff) * roundoff
        if march:
            merged_df['delivery1'] = round(merged_df['Net req up to march'] / roundoff) * roundoff
            if deliverylots == 3:
                merged_df["delivery2"] = round(((merged_df[rounded_column_name] - merged_df['delivery1']) * 0.5) / roundoff) * roundoff
                merged_df["delivery3"] = merged_df[rounded_column_name] - merged_df["delivery1"] - merged_df["delivery2"]
            else:
                merged_df["delivery2"] = merged_df[rounded_column_name] - merged_df["delivery1"]
        else:
            if deliverylots == 3:
                merged_df["delivery1"] = round((merged_df[rounded_column_name] * 0.3) / roundoff) * roundoff
                merged_df["delivery2"] = round((merged_df[rounded_column_name] * 0.3) / roundoff) * roundoff
                merged_df["delivery3"] = merged_df[rounded_column_name] - merged_df["delivery1"] - merged_df["delivery2"]
            else:
                merged_df["delivery1"] = round((merged_df[rounded_column_name] * 0.5) / roundoff) * roundoff
                merged_df["delivery2"] = merged_df[rounded_column_name] - merged_df["delivery1"]
    else:
        if march:
            merged_df['delivery1'] = round(merged_df['Net req up to march'])
            if deliverylots == 3:
                merged_df["delivery2"] = round((merged_df['NPQ'] - merged_df['delivery1']) * 0.5)
                merged_df["delivery3"] = merged_df['NPQ'] - merged_df["delivery1"] - merged_df["delivery2"]
            else:
                merged_df["delivery2"] = merged_df['NPQ'] - merged_df["delivery1"]
        else:
            if deliverylots == 3:
                merged_df["delivery1"] = round(merged_df['NPQ'] * 0.3)
                merged_df["delivery2"] = round(merged_df['NPQ'] * 0.3)
                merged_df["delivery3"] = merged_df['NPQ'] - merged_df["delivery1"] - merged_df["delivery2"]
            else:
                merged_df["delivery1"] = round(merged_df['NPQ'] * 0.5)
                merged_df["delivery2"] = round(merged_df['NPQ'] - merged_df["delivery1"])
        
    
    return merged_df

# Usage:
# Call the function with your DataFrame and parameters
# modified_df = allocate_delivery_quantities(merged_df, roundoff_value, march_value, deliverylots_value)


st.title("Input Form")

# Input for total number of months
total = st.number_input("Total number of months", min_value=1, step=1)

# Input for round off value
roundoff = st.number_input("Enter round off value", min_value=0, step=1)

# Input for up to March or not
march = st.checkbox("Up to March", value=False)

# Input for number of lots
deliverylots = st.number_input("Enter number of lots", min_value=1, step=1)

# Input for splitting required
splitting = st.checkbox("Splitting required", value=False)

if splitting:
    # Input for L1 percent
    splittingp = st.number_input("Enter L1 percent", min_value=0.0, max_value=100.0, step=0.1)

# Display the values
st.write("Total number of months:", total)
st.write("Round off value:", roundoff)
st.write("Up to March:", "Yes" if march else "No")
st.write("Number of lots:", deliverylots)
st.write("Splitting required:", "Yes" if splitting else "No")

if splitting:
    st.write("L1 percent:", splittingp)

#def roundoff(df,a)
df = pd.read_excel('Book1.xlsx',usecols=['Depot code', 'Depot', 'CONSP 20-21','CONSP 21-22','CONSP 22-23','CONSP 23-24','AAC','Stock','Tender quantity','Clubing'],sheet_name='Sheet1')
#df = pd.read_excel('Book1.xlsx',usecols='A,B,F:K')
df1 = pd.read_excel('Book1.xlsx',usecols=['Depot code', 'Due-Qty','Remarks'],sheet_name='Sheet4')
df2 = pd.read_excel('Book1.xlsx',usecols=['Depot', 'UDM stock','Remarks'],sheet_name='UDM')
df1 = df1.dropna()
#desired_rows = df1[df1['Remarks'] == 'Considered' or df1['Remarks'] == 'considered']
df1 = df1[(df1['Remarks'] == 'Considered') | (df1['Remarks'] == 'considered')]
df2 = df2[(df2['Remarks'] == 'Considered') | (df2['Remarks'] == 'considered')]
print(df1.head())
print(df2.head())
df2['UDM stock'] = df2['UDM stock'].str.split('.').str[0].astype(int)
result = df1.groupby('Depot code')['Due-Qty'].sum()
result1 = df2.groupby('Depot')['UDM stock'].sum()
print(result)
print(result1)
df = pd.merge(df, result, on='Depot code', how='left')
df = pd.merge(df, result1, on='Depot', how='left')
df['Due-Qty'].fillna(0, inplace=True)
df['UDM stock'].fillna(0, inplace=True)
df = df.dropna(subset=['AAC'])
print(df.head(10))

#column_to_exclude = ['Tender quantity','Clubing']
columns_to_fill = ['Depot code', 'Depot', 'CONSP 20-21','CONSP 21-22','CONSP 22-23','CONSP 23-24','AAC','Stock']
print(columns_to_fill)
df[columns_to_fill] = df[columns_to_fill].fillna(method='ffill')
#df_filled = df.fillna(method='ffill')
dfAAC = df[df['CONSP 20-21']==0 ]
dfAAC=dfAAC[['Depot', 'AAC']]
dforginal = df[df['CONSP 20-21']!=0]
column_to_drop = 'AAC'
dforginal = dforginal.drop(column_to_drop, axis=1)
merged_df = pd.merge(dforginal, dfAAC, on='Depot', how='inner')
merged_df["MC"]=round(merged_df["AAC"]/12,2)
merged_df["Total req"]=round(merged_df["MC"]*total)
merged_df["Net req"]=round(merged_df["Total req"]-merged_df["Stock"])-merged_df["Due-Qty"]-merged_df["UDM stock"]



# Get today's date
today = datetime.today()

# Define the target date as March 31st of the current year
target_date = datetime(today.year+1, 3, 31)

# Calculate the number of months between today and the target date
months_between = round((target_date.year - today.year) * 12 + (target_date.month - today.month))

# Round off the number of months to the nearest whole number


# Print the result
print(f"Months between today and March 31st (rounded): {months_between} months")

merged_df["Net req up to march"]=round(((months_between*merged_df["MC"])-merged_df["Stock"]-merged_df["Due-Qty"]).apply(lambda x: max(0, x)))

# Assuming you have a DataFrame 'df' and you want to move the column 'column_name' to the last position
column_name = 'Tender quantity'

# Drop the column
column_to_move = merged_df.pop(column_name)

# Insert the column at the last position
merged_df.insert(len(merged_df.columns), column_name, column_to_move)


def split_clubs(x):
    if isinstance(x, str):  # Check if the value is a string
        print(x, 'sprint')
        return x.split(",")
    else:
        return []


column_to_check = 'Clubing'
merged_df['Clubing'] = list(merged_df['Clubing'].apply(split_clubs))
print(merged_df['Clubing'])

is_empty = merged_df[column_to_check].apply(lambda x: len(x) if isinstance(x, list) else 0).eq(0).all()
merged_list = [item for sublist in merged_df['Clubing'].values for item in sublist] 
if is_empty:
    merged_df['NPQ'] = np.where(merged_df['Tender quantity'] > merged_df['Net req'], merged_df['Net req'], merged_df['Tender quantity'])
    print("here")
else:
    for ind, row in merged_df.iterrows():
        print(row["Clubing"], row['Depot'])
        print(merged_df['Clubing'].values)
        if row['Depot'] is not None and row['Depot'] in merged_list:
            merged_df.loc[ind, "NPQ"] = 0
            print("here1", row['Depot'])
        elif isinstance(row["Clubing"], list):
            # Assuming "Clubing" is a list of strings
            club_stock = merged_df[merged_df['Depot'].apply(lambda x: x in row["Clubing"])]
            print(club_stock, 'king')
            if not club_stock.empty:
                total_club_stock = club_stock['Net req'].sum()
                merged_df.loc[ind, "NPQ"] = row["Net req"] + total_club_stock
            else:
                merged_df.loc[ind, "NPQ"] = row["Net req"]
        elif pd.isna(row["Clubing"]):
            merged_df.loc[ind, "NPQ"] = row["Net req"]
            print("here2", row['Depot'])
        else:
            club_stock = merged_df[merged_df['Depot'].apply(lambda x: x == row["Clubing"])]['Net req'].values
            if len(club_stock) > 0:
                merged_df.loc[ind, "NPQ"] = row["Net req"] + club_stock[0]
                print("here2", row['Depot'])
    merged_df['NPQ'] = np.where(merged_df['Tender quantity'] > merged_df['NPQ'], merged_df['NPQ'], merged_df['Tender quantity'])
#formatting and total
    
merged_df = allocate_delivery_quantities(merged_df, roundoff, march, deliverylots)
if(splitting):
        merged_dfk=pd.DataFrame.copy(merged_df)
        merged_dfk['NPQ'] = (merged_df['NPQ'].astype(float) * splittingp)
        merged_dfk['Net req up to march'] = (merged_df['Net req up to march'].astype(float) * splittingp)
        print(merged_dfk['NPQ'])
        merged_df1 = allocate_delivery_quantities(merged_dfk, roundoff, march, deliverylots)
        merged_df["firm1 d1"] = merged_df1["delivery1"]
        merged_df["firm1 d2"] = merged_df1["delivery2"]                            
        if(deliverylots==3):
            merged_df["firm1 d3"] = merged_df1["delivery3"]
        """merged_dfp=pd.DataFrame.copy(merged_df)
        merged_dfp['NPQ'] =( merged_df['NPQ'].astype(float) * (1-splittingp))
        merged_dfp['Net req up to march'] = merged_df['Net req up to march'].astype(float) * (1-splittingp)
        merged_df2 = allocate_delivery_quantities(merged_dfp, roundoff, march, deliverylots)
        merged_df["firm2 d1"] = merged_df2["delivery1"]
        merged_df["firm2 d2"] = merged_df2["delivery2"]                            
        if(deliverylots==3):
            merged_df["firm2 d3"] = merged_df2["delivery3"]"""
       
        merged_df["firm2 d1"] = merged_df['delivery1']-merged_df["firm1 d1"]
        merged_df["firm2 d2"] = merged_df['delivery2']-merged_df["firm1 d2"]
        if(deliverylots==3):
            merged_df["firm2 d3"] = merged_df['delivery3']-merged_df["firm1 d3"]    
        
''''if(roundoff!=0):
    merged_df['NPQ rounded off to'+ str(roundoff)]=round(merged_df['NPQ']/roundoff)*roundoff
    if(march):
        merged_df['delivery1']=round((merged_df['Net req up to march'])/roundoff)*roundoff
        if(deliverylots==3):
            merged_df["delivery2"]=round(((merged_df['NPQ rounded off to'+ str(roundoff)]-merged_df['delivery1'])*0.5)/roundoff)*roundoff
            merged_df["delivery3"]=merged_df['NPQ rounded off to'+ str(roundoff)]-merged_df["delivery1"]-merged_df["delivery2"]
        else:
             merged_df["delivery2"]=merged_df['NPQ rounded off to'+ str(roundoff)]-merged_df["delivery1"]
    else:
        if(deliverylots==3):
            merged_df["delivery1"]=round(((merged_df['NPQ rounded off to'+ str(roundoff)])*0.3)/roundoff)*roundoff
            merged_df["delivery2"]=round(((merged_df['NPQ rounded off to'+ str(roundoff)])*0.3)/roundoff)*roundoff
            merged_df["delivery3"]=merged_df['NPQ rounded off to'+ str(roundoff)]-merged_df["delivery1"]-merged_df["delivery2"]
        else:
            merged_df["delivery1"]=round((merged_df['NPQ rounded off to'+ str(roundoff)]*0.5)/roundoff)*roundoff
            merged_df["delivery2"]=merged_df['NPQ rounded off to'+ str(roundoff)]-merged_df["delivery1"]
else:
    if(march):
        merged_df['delivery1']=round(merged_df['Net req up to march'])
        if(deliverylots==3):
            merged_df["delivery2"]=round((merged_df['NPQ']-merged_df['delivery1'])*0.5)
            merged_df["delivery3"]=merged_df['NPQ']-merged_df["delivery1"]-merged_df["delivery2"]
        else:
            merged_df["delivery2"]=merged_df['NPQ']-merged_df["delivery1"]
        
    else:
        if(deliverylots==3):
            merged_df["delivery1"]=round(merged_df['NPQ']*0.3)
            merged_df["delivery2"]=round(merged_df['NPQ']*0.3)
            merged_df["delivery3"]=merged_df['NPQ']-merged_df["delivery1"]-merged_df["delivery2"]
        else:
            merged_df["delivery1"]=round(merged_df['NPQ']*0.5)
            merged_df["delivery2"]=round(merged_df['NPQ']-merged_df["delivery1"])'''
    #merged_df["delivery3"]=round(merged_df['NPQ']*0.5)
merged_df.loc['total'] = merged_df.select_dtypes(np.number).sum()
merged_df['Depot code']=merged_df['Depot code'].astype(int)
merged_df['Stock']=merged_df['Stock'].astype(int)
merged_df['Depot'] = merged_df['Depot code'].astype(str)+'-' + merged_df['Depot'].astype(str)
merged_df = merged_df.drop(['Depot code','Clubing'], axis=1)
merged_df.at[merged_df.index[-1], 'Depot'] ="Total"
last_row_value = merged_df.loc[merged_df.index[-1], 'Stock']
last_row_valueA = merged_df.loc[merged_df.index[-1], 'AAC']
months=round((last_row_value/last_row_valueA)*12,2)
print(months)
new_str_value = str(last_row_value)+'('+str(months)+' months)'
merged_df['Stock']=merged_df['Stock'].astype(str)
merged_df.at[merged_df.index[-1], 'Stock'] =new_str_value
# Display the DataFrame with the total row
print(merged_df)
#merged_df=
excel_file = 'output_data.xlsx'
merged_df.to_excel(excel_file, index=False)  # Set index=False to exclude the index column

# Confirm that the data is saved to the Excel file
print(f'Data saved to {excel_file}')





