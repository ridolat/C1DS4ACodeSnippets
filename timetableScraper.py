from bs4 import BeautifulSoup
import requests
import urllib.request


def main():
	schedules_url = "https://new.mta.info/schedules"
	timetable_url = "https://new.mta.info"

	

	#Use BeautifulSoup to scrape webpage content from schedules website
	r = requests.get(schedules_url)
	soup = BeautifulSoup(r.content, 'html.parser')
	all_elements = soup.find_all("div", {"class": "field--item"})
	

	#Designate the train line timetables we're going to be scraping
	train_lines_used = ['1 train', '6 train', 'A train', 'C train', 'B train', 'D train', 'N train', 'Q train', 'R train', 'W train']

	#Get all the elements on the schedules page with anchor elements(links)
	list_of_elements_with_anchor = []
	for element in all_elements:
		if(element.findChildren("a", recursive= False)):
			list_of_elements_with_anchor.append(element)


	

	#From the earlier list, we will get all of the href's of those anchor elements who's text matches the train lines we're looking for.
	list_of_timetable_hrefs = []
	count = 0
	for element in list_of_elements_with_anchor:	
		for train in train_lines_used:
			if(element.get_text(strip=True) == train):
				anchor = element.find('a')
				# print(anchor.get('href'))
				list_of_timetable_hrefs.append(anchor.get('href'))



	
	#Download each of the pdfs we're looking for that match up with our designated trains.
	for i in range(0, len(list_of_timetable_hrefs)):
		download_url = timetable_url + list_of_timetable_hrefs[i]
		r = requests.get(download_url, stream=True)

		#Write the pdfs to file, using train line names!
		with open(train_lines_used[i]+"_timetable.pdf", "wb") as f:
			f.write(r.content)







if __name__ == "__main__":
	main()




