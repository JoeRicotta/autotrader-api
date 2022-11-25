from autotrader import CarSearch
import webbrowser


search = CarSearch("toyota", "camry")

CarSearch.numRecords = 50

search.search()

print(search.results[0:20])

dir(search.results[4])

search.results[4].open()


