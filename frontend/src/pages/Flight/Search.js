import React, { useEffect, useState } from "react";
import Result from "./Result";
import axios from "axios";

function Search() {
  const [btnType, setbtnType] = useState("oneWay");
  const [bookReturn, setBookReturn] = useState(false);

  const [originCity, setOriginCity] = useState("");
  const [destinationCity, setDestinationCity] = useState("");
  const [departureDate, setDepartureDate] = useState("");
  const [returnDate, setReturnDate] = useState("");
  const [cabinClass, setCabinClass] = useState("Economy"); // ["Economy", "Business", "First"
  const [filteredData, setFilteredData] = useState([]);

  const [isSearchClicked, setIsSearchClicked] = useState(false);
  const [returnFilterData, setReturnFilterData] = useState([]);

  const bookType = [
    {
      name: "One Way",
      id: "oneWay",
    },
    {
      name: "Round Trip",
      id: "roundTrip",
    },
  ];

  const handleBookType = (id) => {
    setbtnType(id);
    if (id === "oneWay") {
      setIsSearchClicked(false);
      setBookReturn(false);
      setReturnDate("");
    } else if (id === "roundTrip") {
      setIsSearchClicked(false);
      setBookReturn(true);
    }
  };

  const handleFocus = (e) => {
    e.currentTarget.type = "date";
  };
  const handleBlur = (e) => {
    e.currentTarget.type = "text";
  };

    const handleFilter = async () => {
        try {
            // Make a database call to check for a flight
            const response = await axios.get(`http://localhost:8000/flight/internal_search/oneway/${originCity}/${destinationCity}/${departureDate}/${cabinClass}`);
            const flightData = response.data;

            if (flightData !== null) {
                // Flight found in the database, return the data
                setFilteredData(flightData);
            } else {
                // Flight not found in the database, make an API call, will then populate the database
                let apiResponse
                if (bookReturn && returnDate) {
                    apiResponse = await axios.get(`http://localhost:8000/flight/external_search/round/${originCity}/${destinationCity}/${departureDate}/${returnDate}/${cabinClass}`);
                } else {
                    apiResponse = await axios.get(`http://localhost:8000/flight/external_search/oneway/${originCity}/${destinationCity}/${departureDate}/${cabinClass}`);
                }
                const externalFlightData = apiResponse.data;

                // Make the database call again
                const updatedResponse = await axios.get(`http://localhost:8000/flight/internal_search/oneway/${originCity}/${destinationCity}/${departureDate}/${cabinClass}`);
                const updatedFlightData = updatedResponse.data;

                if (updatedFlightData == null) {
                    // No matching flights found
                    alert("No matching flights found for your criteria.");
                }

                setFilteredData(updatedFlightData);
            }
        } catch (error) {
            console.error("Error:", error);
        }
    };
    const returnFilter = async () => {
        try {
            // Make a database call to check for a flight
            const response = await axios.get(`http://localhost:8000/flight/internal_search/oneway/${destinationCity}/${originCity}/${returnDate}/${cabinClass}`);
            const flightData = response.data;

            if (flightData !== null) {
                // Flight found in the database, return the data
                setReturnFilterData(flightData);
            } else {
                // No matching flights found
                alert("No matching flights found for your criteria.");
            }
        } catch (error) {
            console.error("Error:", error);
        }
    };


  const handleSearch = () => {
    if (bookReturn && !returnDate) {
      alert("You must specify a Return Date!");
    } else if (!originCity) {
      alert("You must specify an Origin!");
    } else if (!destinationCity) {
      alert("You must specify a Destination!");
    } else if (!departureDate) {
      alert("You must specify a Departure Date!");
    }
    if (originCity && destinationCity && departureDate) {
      setIsSearchClicked(true);
      handleFilter();
      if (bookReturn && returnDate) {
        returnFilter();
      }
    }
  };

  return (
    <div>
      <div className="row mt-4 ml-5 mr-5">
        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <div className="card">
                <div className="card-body">
                  <div className="btn-group d-flex justify-content-center">
                    {bookType.map((type) => {
                      return (
                        <button
                          type="button"
                          className={`btn ${
                            btnType === type.id ? "active_btn" : ""
                          }`}
                          key={type.id}
                          onClick={() => handleBookType(type.id)}
                        >
                          {type.name}
                        </button>
                      );
                    })}
                  </div>
                  <input
                    type="text"
                    placeholder="Enter Origin Airport"
                    className="form-control mt-4"
                    onChange={(e) => setOriginCity(e.target.value)}
                  />
                  <input
                    type="text"
                    placeholder="Enter Destination Airport"
                    className="form-control mt-2"
                    onChange={(e) => setDestinationCity(e.target.value)}
                  />
                  <input
                    type="date"
                    placeholder="Enter departure date"
                    className="form-control mt-2"
                    onFocus={handleFocus}
                    onBlur={handleBlur}
                    onChange={(e) => setDepartureDate(e.target.value)}
                  />
                  {btnType === "roundTrip" ? (
                    <input
                      type="date"
                      placeholder="Enter return date"
                      className="form-control mt-2"
                      onFocus={handleFocus}
                      onBlur={handleBlur}
                      onChange={(e) => setReturnDate(e.target.value)}
                    />
                  ) : null}
                  <select
                      className="form-control mt-2"
                      onChange={(e) => setCabinClass(e.target.value)}
                  >
                  <option value="">Select Cabin Class</option>
                  <option value="ECONOMY">ECONOMY</option>
                  <option value="BUSINESS">BUSINESS</option>
                  <option value="FIRST">FIRST</option>
                  </select>
                  <div>
                    <button
                      type="button"
                      className="btn search_btn"
                      onClick={handleSearch}
                    >
                      <b>Search</b>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-8">
          <Result
            filteredData={filteredData}
            bookReturn={bookReturn}
            isSearchClicked={isSearchClicked}
            returnFilterData={returnFilterData}
          />
        </div>
      </div>
    </div>
  );
}

export default Search;