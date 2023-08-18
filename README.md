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



| ![Average Elo Disparity](https://github.com/AlfiePerkins1/FaceitStats/assets/28139876/0831c55c-968e-4190-9ce1-5b0a437e705f) | 
|:--:| 
| *Average Elo Disparity* |



| ![image](https://github.com/AlfiePerkins1/FaceitStats/assets/28139876/31bfd2ca-7b36-4333-9130-a7c6e0aaca88) | 
|:--:| 
| *Elo compared with games Graph* |

