# FaceitStats


A python project which uses the official [Faceit API](https://developers.faceit.com/docs/tools/data-api) to return stats about the user.

Currently supported:
1. Average Elo disparity within users games
2. Elo chart with Elo on the Y axis and games played on the X axis


Libraries used:

- Requests | For accessing API's
- json | For converting to json format
- matplotlib | For displaying the data in a visual format(Graphs)
- Numpy | For calculating a regression line with 1 polynomial degree
- Pandas | For dataframe manipulation
- BeautifulSoup | For web scraping data when API isnt avaliable
- time | For adding an interval to each round of web scraping as to not get timedout


## ToDo

* Multithreading to speed up API requests as it currently takes about 30 seconds to get the data to draw the Average Elo Disparity chart
* Make use of more data avaliable from the official Faceit API as to not rely on web scraping
* Implement more graphs and options


## Example Graphs


| ![Average Elo Disparity](https://github.com/AlfiePerkins1/FaceitStats/assets/28139876/d4824ab6-1dda-452e-a476-a5300d0cd147) | 
|:--:| 
| *Average Elo Disparity* |



| ![Elo compared with games](https://github.com/AlfiePerkins1/FaceitStats/assets/28139876/972e4def-e1be-47c6-9628-dd233f534afb) | 
|:--:| 
| *Elo compared with games Graph* |

