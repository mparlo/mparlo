#!/usr/bin/env python
# coding: utf-8

# In[1]:


#loading pandas and numpy
import pandas as pd
import numpy as np


# In[2]:


#reading data into pandas
path = 'C:\\Users\\PC\\Downloads\\DOB LL84_133 Data Quality Error Log 2021 (DQE) - Sheet1.csv'

LL84Data = pd.read_csv(path,dtype='object')


# In[3]:


#printing info on the data for a quick manual check
#print (LL84Data.head())
#print(LL84Data.info())


# In[4]:


#dropping columns that aren't useful for our analysis to make it run faster
Submission_Data = LL84Data.drop(LL84Data.columns[27:52],axis=1)


# In[5]:


#printing info on the data for a quick manual check
#print (Submission_Data.head())
#print(Submission_Data.info())
#print (Submission_Data.nunique())

#separating out submissions that have missing BBLs
Missing_BBL = Submission_Data[Submission_Data['Cleaned BBL'] == "NotAvailable"]
Submission_Data = Submission_Data[Submission_Data['Cleaned BBL'] != "NotAvailable"]

Missing_BBL.to_csv("Submissions Missing BBL.csv")


# In[6]:


#separating individual properties and printing info on the data for a quick manual check
Individual_Props = Submission_Data[Submission_Data['Parent Property ID'] == "Not Applicable: Standalone Property"]
#print(Individual_Props.head())
#print(Individual_Props.info())
#print (Individual_Props.nunique())

#filtering Individual_Props for BBLs greater than 10 digits and separating them into a dataframe
Individual_Props['BBL_Length']  = Individual_Props['Cleaned BBL'].str.len()
Incorrect_BBLs = Individual_Props[Individual_Props['BBL_Length'] != 10]
Individual_Props = Individual_Props[Individual_Props['BBL_Length'] == 10]
Individual_Props.to_csv("Individual Property Submissions.csv")
Incorrect_BBLs.to_csv("Submissions with Incorrect BBLs.csv")


# In[7]:


#separating campus/parent-child properties and printing info on the data for a quick manual check
Parent_Child_Props = Submission_Data[Submission_Data['Parent Property ID'] != "Not Applicable: Standalone Property"]
#print (Parent_Child_Props.head())
#print(Parent_Child_Props.nunique())
#print(Parent_Child_Props.info())


# In[8]:


#building out some code to clean columns. 
#right now it just removes any punctuation/symbols left over in the columns, but there are some BBLs that were entered very
#incorrectly (entering the borough by name and not number, for example). We'll have to figure out how to fix those BBL outliers
import string

punct = """ '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{}~' """   # `|` is not present here
transtab = str.maketrans(dict.fromkeys(punct, ''))

column_cleanup = ['BBL','Cleaned BBL','GFA on CBL']

#Individual_Props['BBL'] = '|'.join(Individual_Props['BBL'].tolist()).translate(transtab).split('|')
#Individual_Props['Cleaned BBL'] = '|'.join(Individual_Props['Cleaned BBL'].tolist()).translate(transtab).split('|')
#Individual_Props['GFA on CBL'] = '|'.join(Individual_Props['GFA on CBL'].tolist()).translate(transtab).split('|')

for column in column_cleanup:
    Individual_Props[column] = '|'.join(Individual_Props[column].tolist()).translate(transtab).split('|')


# In[9]:


#checking number of unique values in each Individual property column before filtering
#print (Individual_Props.nunique())


# In[49]:


#submitter_counts = Individual_Props.groupby(['Cleaned BBL','BIN'])['Property ID'].nunique().sort_values(ascending = False)
#submitter_counts[submitter_counts > 1]

#emaildate_counts = Individual_Props.groupby(['Cleaned BBL','Property ID','BIN'])['Release Date'].nunique().sort_values(ascending=False)
#emaildate_counts[emaildate_counts>1]

#Level 1 filter - creates a column with the number of unique property IDs for each cleaned BBL and filters dataset for BBLs with more than one Property ID
Individual_Props['Property ID Count (per BBL)'] = Individual_Props.groupby(["Cleaned BBL"])["Property ID"].transform('nunique')
Individual_Props.to_csv("Property ID Screen Test.csv")
Multiple_PropIDs = Individual_Props[Individual_Props['Property ID Count (per BBL)'] > 1]

#Level 2 filter - creates a column with the number of unique BINs for each cleaned BBL and filters dataset for BBLs with more than one BIN
Multiple_PropIDs['BIN Count (per BBL)'] = Multiple_PropIDs.groupby(["Cleaned BBL"])["BIN"].transform('nunique')
Multiple_PropIDs.to_csv("BIN Screen Test.csv")
Multiple_PropIDs_BINs = Multiple_PropIDs[Multiple_PropIDs["BIN Count (per BBL)"] >1 ]

#Level 3 filter - creates a column with the number of Submission Dates for each cleaned BBL and filters dataset for BBLs with more than one Submission Date
Multiple_PropIDs_BINs['Submission Date Count (per BBL)'] = Multiple_PropIDs_BINs.groupby(["Cleaned BBL"])["Release Date"].transform('nunique')
Multiple_PropIDs_BINs.to_csv("Submission Date Screen Test.csv")
Multiple_PropIDs_BINs_Subs = Multiple_PropIDs_BINs[Multiple_PropIDs_BINs['Submission Date Count (per BBL)'] >1 ]

print(Multiple_PropIDs_BINs_Subs)


# 
# dist_propid	Total distinct property_ids associated with the cleaned BBL -- count > 1 here could indicate dup
# dist_bin	Total distinct bins associated with cleaned BBL -- count > 1 here could indicate a campus/child relationship
# dist_date	Total count of distinct dates associated with submissions -- count > 1 here could indicate dup
# dist_email	Total count of distinct email addresses associated with submission -- count > 1 here could indicate dup
# 	
# Filter Down Logic:	
# 1. Start with count dist_propid > 1 and review results	
# Result:	
# 1252 rows	168 child properties
# 2. Remove child properties and associated BBLs and check next column for count of distinct bin	
# Result:	
# 247 rows	
# 3. Filter on dist_date > given that a single date should indicate one submission for each BBL so far	
# Result:	
# 203 rows	
# 4. Take list of 203 cleaned BBLs after filtering and pull all associated metadata from the full submission table	
# Result:	
# 994 total rows -- these show all duplicate entries and each cleaned_bbl appears more than once	
# 	
# Everything remaining in worksheet after_filter_4 should be a duplicate entry --> even if one person submitted more than once (not technically dup), the BBL should be there because another person also submitted (different email address + property_id).

# In[13]:


#UNUSED CODE

#limit = 1
#submitter_count = submitter_counts[submitter_counts > limit].count()
#submitter_count
#Individual_Props.groupby(['Cleaned BBL']).apply(lambda grp: grp.groupby('Property ID')['Cleaned BBL'].count().to_dict()).to_dict()


# In[14]:


#remove any rows where BBL/BIN are NotAvailable
#get a count of outlier BBLs and make a list of what they look like. maybe filter out rows with multiple BBLs?

