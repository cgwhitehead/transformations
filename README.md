# Transformations
A brief set of python functions for transforming en ef el data for optimization

## Purpose
When trying to run analysis for my fantasy team, I always  ended up with a bunch of odd csv/excel sheets. This is an example of a series of functions I use to clean, transform, and combine data sources.

## Setup
* Download salary csv from Draft Kings dot com. 
* Download play by play data from (nflsavant.com)

## Use
The files DKSalaries.csv and pbp-2018.csv should be in your working directory. Import ftbl_etl and call football_etl with a list of injured players. 
```
import ftbl_etl as etl

injured_players = ['j.flacco', 'a.dalton']

```
