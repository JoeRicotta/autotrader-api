import requests
import json
from pprint import pp


#https://www.autotrader.com/cars-for-sale/certified-cars/sedan/kia/optima/bellefonte-pa-16823?requestId=614960940&maxMileage=60000&transmissionCodes=AUT&searchRadius=50&maxPrice=20000&marketExtension=include&endYear=2018&startYear=2013&isNewSearch=true&showAccelerateBanner=false&sortBy=relevance&numRecords=25

class CarSearch:

    numRecords = 25

    def __init__(self,
                 make = None,
                 model = None,
                 endYear = None,
                 startYear = None,
                 city = None,
                 state = None,
                 zip_ = None,
                 requestID = None,
                 maxMileage = None,
                 transmissionCodes = None,
                 searchRadius = None,
                 maxPrice = None):

        self._make = make
        self._model = model
        self._check_make_model()
        
        self._city = city
        self._state = state
        self._zip = zip_
        self._check_loc()
        
        self.requestID = requestID
        self.maxMileage = maxMileage
        self.transmissionCodes = transmissionCodes
        self.searchRadius = searchRadius
        
        self.maxPrice = maxPrice
        
        self.endYear = endYear
        self.startYear = startYear
        
        self._is_searched = False
        self.results = None

    def _check_make_model(self):
        self._pass_make = self._make is not None
        self._pass_model = self._model is not None
        if not self._pass_make and self._pass_model:
            raise(ValueError("Must pass make if you pass model."))
        
    def _check_loc(self):
        locs = [self._city, self._state, self._zip]
        if all([x is None for x in locs]):
            self._pass_loc = False
        elif all([x is not None for x in locs]):
            self._pass_loc = True
        else:
            raise(ValueError("Please enter city, state and zip altogether when creating search."))

    @staticmethod
    def _is_payload(x):
        is_underline = x[0][0] == "_"
        isnt_none = x[1] is not None
        isnt_result = x[0] != "results"
        return is_underline and isnt_none and isnt_result
        
    def search(self, **kwargs):
        """ request cars from autotrader, kwargs ignored """
        
        # reassign searched value
        if not self._is_searched:
            self._is_searched = True
            self._page = 1

        # get new url
        base_url = "https://www.autotrader.com/cars-for-sale/"

        # build url
        if self.requestID is not None:
            # all-cars, certified-cars, etc.
            base_url += self.requestID + "/"
        if self.maxPrice is not None:
            base_url += f"cars-under-{self.maxPrice}" + "/"
        if self._pass_make:
            base_url += self._make  + "/"
        if self._pass_model:
            base_url += self._model + "/"
        if self._pass_loc:
            base_url += self._city + "-" + self._state + "-" + self._zip

        # begin queries
        payload = dict([x for x in self.__dict__.items() if self._is_payload(x)])

        # updating with special values
        payload.update({"numRecords" : CarSearch.numRecords})
        payload.update(kwargs)

        # getting request
        r = requests.get(base_url, params = payload)

        # formatting return value for easy reading
        init_ = '<script data-cmp="lstgSchema" type="application/ld+json">'
        split_ = r.text.split(init_)
        inds_ = [self._bracket_inds(x) for x in split_]
        loads_ = [json.loads(x[i[0]:i[1]]) for x,i in zip(split_, inds_)]
        loads_ = [x for x in loads_ if len(x.keys()) > 0]
        
        # adding attributes
        self.n_results = len(loads_)
        self.results = [Car(x) for x in loads_]
        return self

    @staticmethod
    def _bracket_inds(s):
        """ takes string and returns index of starting and ending json bracket indices"""
        cnt = 0
        begin = False
        for i,x in enumerate(s):
            if x == "{":
                if not begin:
                    j = i
                begin = True
                cnt += 1
            elif x == "}":
                if not begin:
                    continue
                cnt -= 1
            if begin and cnt == 0:
                return j, i+1

    def next(self):
        """ continue to next page """
        self._page += 1
        self.search(firstRecord = CarSearch.numRecords * self._page)
        return self

    def go_to(self, page_n):
        """ go to specific page """
        self._page = page
        self.search(firstRecord = CarSearch.numRecords * self._page)
        return self

    def prev(self):
        """ continue to prev page """
        if self._page == 1:
            raise(ValueError("Cannot go back, on first page currently."))
                  
        self._page -= 1
        self.search(firstRecord = CarSearch.numRecords * self._page)
        return self


class Car:

    def __init__(self, args):
        self.__dict__ = args

    def __repr__(self):
        return f"<{self.name}: {self.vehicleIdentificationNumber}, ${self.offers['price']}>"


# testing
cur = __name__
if cur == "__main__":
    # checking keys
    search = CarSearch(state = "pa", city = "bellefonte", zip_ = "16823",
                       make = "ford", maxPrice = 25000, maxMileage = 50000,
                       searchRadius = "500", requestID = "all-cars")
    search.search()
    for x in search.results:
        pp(x)



