import tabula
import os
import numpy as np
import camelot
from pikepdf import Pdf
import pandas as pd
import glob
import sys


def find_time_difference(startTime, endTime):

	start_list = startTime.split(':')
	end_list = endTime.split(':')

	# print(start_list)
	# print(end_list)
	print("START TIME: " + str(start_list))
	print("END TIME: " + str(end_list))

	#Check if hour of end time is less than start, to support 12hr time
	if (int(end_list[0]) < int(start_list[0])):
		end_list[0] = (int(end_list[0])) + 12		

	start_mins = int(start_list[0])*60 + int(start_list[1][:2])
	end_mins = int(end_list[0])*60 + int(end_list[1][:2])


	# print("DIFFERENCE IN TIME = " + str(end_mins - start_mins))
	difference = abs(end_mins - start_mins)
	return difference

def unencrypt_timetable_pdfs():
	# os.mkdir("unencrypted_timetable_pdfs")
	list_of_timetables = []
	
	for file in glob.glob("*.pdf"):
		# print(file)
		list_of_timetables.append(file)
		with Pdf.open(file) as pdf:
			pdf.save("unencrypted_timetable_pdfs/" + "ue_" + file)

	return list_of_timetables





def remove_special_characters(dataframe_in):
	for i in range(0, len(dataframe_in)):
		dataframe_in[i].df = dataframe_in[i].df.replace(r'\n',  '', regex=True)

	dataframe_out = dataframe_in 	
	return dataframe_out



def clean_mta_timetable(dataframe_in):

	#Concat all pages of the timetable into 1 dataframe
	# print(dataframe_in[0])
	df = pd.concat([dataframe_in[i].df for i in range(0, len(dataframe_in))], ignore_index=True)


	#Identify rows to delete to get rid of Saturday and Sunday train schedule

	try:
		if((df[df[0].str.contains("Saturday")].index[0])):
			index_of_weekend_data = (df[df[0].str.contains("Saturday")].index[0])

			#DF with Weekend eliminatd and duplicated rows too

			#Drop rows that have weekend data
			df.drop(df.index[index_of_weekend_data:len(df.index)+1], inplace=True)
	except IndexError as error:
		print("No Weekend data")
	


	try:
		if((df[df[0].str.contains("Travel")].index[0])):
			index_of_travel_info = (df[df[0].str.contains("Travel")].index[0])

			#DF with Weekend eliminatd and duplicated rows too

			#Drop rows that have weekend data
			df.drop(df.index[index_of_travel_info:len(df.index)+1], inplace=True)
	except IndexError as error:
		print("No Travel Advisory data")
	




	#Drop duplicate rows (the duplicated rows are only stop names. No other rows are duplicated.)
	df = df.drop_duplicates(ignore_index=True)



	

	#Split DF into 2 - trips going to, and trips coming from
	row_index = (df[df[0].str.contains("Weekday")].index[1])
	# print(first_split)


	dataframe_list = []

	df_trips_to = df.iloc[:row_index]
	df_trips_from = df.iloc[row_index:]

	new_header = df_trips_to.iloc[1]
	df_trips_to = df_trips_to[2:]
	df_trips_to.columns = new_header

	#if first column has local, mask / delete it
	df_trips_to = df_trips_to.loc[:, ~(df_trips_to == "local").any()]
	df_trips_to = df_trips_to.loc[:, ~(df_trips_to == "*").any()]
	df_trips_to = df_trips_to.loc[:, ~(df_trips_to == "ﬂ+").any()]
	df_trips_to = df_trips_to.loc[:, ~(df_trips_to == "BX-X").any()]


	new_header = df_trips_from.iloc[1]
	df_trips_from = df_trips_from[2:]
	df_trips_from.columns = new_header



	df_trips_from = df_trips_from.loc[:, ~(df_trips_from == "local").any()]
	df_trips_from = df_trips_from.loc[:, ~(df_trips_from == "*").any()]
	df_trips_from = df_trips_from.loc[:, ~(df_trips_from == "ﬂ+").any()]
	df_trips_from = df_trips_from.loc[:, ~(df_trips_from == "BX-X").any()]

	df_trips_from.dropna(axis=1, how='all', inplace=True)
	df_trips_to.dropna(axis=1, how='all',  inplace=True)

	# df_trips_to = df_trips_to.replace('-', np.NaN, regex=True) 
	# df_trips_from = df_trips_from.replace('-', np.NaN, regex=True) 

	dataframe_list.append(df_trips_to)
	dataframe_list.append(df_trips_from)


	return dataframe_list







#MAIN LOGIC
directoryToCreate = os.getcwd()
directoryToCreate = os.getcwd() + "/unencrypted_timetable_pdfs"
# print(directoryToCreate)
os.mkdir(directoryToCreate)

timetables = unencrypt_timetable_pdfs()


column_names = ["train_name", "train_origin", "train_destination", "start_time", "end_time", "time_difference"]


final_destination = ""
train_origin = ""
train_start = ""
train_end = ""

list_of_lists = []
row_list = []
count = 0


for timetable in timetables:
	pdf_path = "unencrypted_timetable_pdfs/" + "ue_" + timetable


	print("Cleaning/Working with Timetable: " + timetable)
	dataframe_raw = camelot.read_pdf(pdf_path, pages="1-end")

	dataframe_clean = remove_special_characters(dataframe_raw)




	dfList = clean_mta_timetable(dataframe_clean)

	for index, row in dfList[0].iterrows():
	

		# df_final["train_name"] = "C"	
		row_list.append(timetable[0].upper())


		for i in dfList[0].columns:
			if(row[i] != "-" and final_destination == ""):
				# print("USE THIS COLUMN TITLE!")
				train_origin = i
				train_start = row[i]

				# print("TRAIN ORIGIN: " + trainOrigin)


				#find destination
				for j in dfList[0].columns[count+1:]:
					# print(dfList[0].columns)
					if(row[j] != "-"):
						final_destination = j
						train_end = row[j]
						# print("ASSIGNING FINAL D: " + str(final_destination))
			count += 1




		difference_in_time = find_time_difference(train_start, train_end)
		#Create list of lists - can't grow dataframe
		row_list.extend([train_origin, final_destination, train_start, train_end, difference_in_time])
		print(row_list)
		list_of_lists.append(row_list)
		

		#Reset Variables
		final_destination = ""
		train_origin = ""
		train_start = ""
		train_end = ""
		row_list = []
		count = 0

	for index, row in dfList[1].iterrows():
	

		# df_final["train_name"] = "C"	
		row_list.append(timetable[0].upper())


		for i in dfList[1].columns:
			if(row[i] != "-" and final_destination == ""):
				train_origin = i
				train_start = row[i]


				#find destination
				for j in dfList[1].columns[count+1:]:
					if(row[j] != "-"):
						final_destination = j
						train_end = row[j]
			count += 1

		
		difference_in_time = find_time_difference(train_start, train_end)
		#Create list of lists - can't grow dataframe
		row_list.extend([train_origin, final_destination, train_start, train_end, difference_in_time])
		print(row_list)
		list_of_lists.append(row_list)
		

		#Reset Variables
		final_destination = ""
		train_origin = ""
		train_start = ""
		train_end = ""
		row_list = []
		count = 0
	

df_final = pd.DataFrame(list_of_lists, columns=column_names)
# print(df_final)
df_final.to_csv("mtaOfficialTimetables.csv", index=False)







