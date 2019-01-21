#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 17:31:44 2018
This is a transformation script for the raw 
play by play data available from http://nflsavant.com/about.php
and combine it with a dr'f'k'ngs salary file
@author: cgwhitehead
"""
import petl as etl
import re
import pandas as pd
import numpy as np

##Global Variables
Team_Map={'NE':'Patriots','GB':'Packers','DET':'Lions','SEA':'Seahawks','LAC':'Chargers','MIN':'Vikings','LA':'Rams'
,'NO':'Saints','MIA':'Dolphins','NYJ':'Jets','CAR':'Panthars','TB':'Buccaneers','DEN':'Broncos','ATL':'Falcons'
,'WAS':'Redskins','BUF':'Bills','CHI':'Bears','KC':'Chiefs','CLE':'Browns','PIT':'Steelers'
,'BAL':'Ravens','SF':'49ers','OAK':'Raiders','ARI':'Cardinals','IND':'Colts','NYG':'Giants','PHI':'Eagles'
,'JAX':'Jaguars','CIN':'Bengals','DAL':'Cowboys','TEN':'Titans','HOU':'Texans'}  

Inverse_Team_Map={v: k for k, v in Team_Map.items()}

##cleaning functions
def parse_description(play):
    r=re.compile('(\d+-\D.\w+)')
    players = r.findall(play)
    return players

def get_yards(play):
    r2=re.compile('(?<=FOR\s)-?\d+')
    r3=re.compile('INCOMPLETE')
    r4=re.compile('(\d+)\sYARD')   
    if r3.search(play):
        return 0
    else:
        yards = r2.findall(play)
        if len(yards)<1:
            return 0
        elif len(yards)>1:
            yards2=r4.search(play)
            if yards2!=None:
                return int(yards2.groups(1)[0])
            else:
                return 999999
        else:
            return int(yards[0])

def clean_rush(row):
    Game = row.GameDate+row.OffenseTeam+row.DefenseTeam
    Team = row.OffenseTeam
    Player = row.p1
    new_rows = []
    new_rows.append([Game,Team,Player,'RUSH YARDS',row.yards])
    if row.IsTouchdown == '1':
        new_rows.append([Game,Team,Player,'RUSH TD',1])
        new_rows.append([Game,row.DefenseTeam,row.DefenseTeam,'POINT ALLOWED',1])
    return pd.DataFrame(new_rows, columns = ['Game', 'Team', 'Player', 'Play', 'Play_Value'])

def fumble(row):
    r=re.compile('(\w{2,3}?)-\d+-\D.\w+')
    desc=r.search(row.Description)
    Game = row.GameDate+row.OffenseTeam+row.DefenseTeam
    Team = row.OffenseTeam
    new_rows = []
    new_rows.append([Game,Team,row.p1,'FUMBLE',1])
    if desc!=None and desc.group(1)==row.DefenseTeam:
        new_rows.append([Game,row.DefenseTeam,row.DefenseTeam,'FUMBLE RECOVERY', 1])
        if row.IsTouchdown == '1':
            new_rows.append([Game,row.DefenseTeam,row.DefenseTeam,'FUMBLE RECOVERY TD', 1])
    elif row.IsTouchdown=='1':
        new_rows.append([Game,row.OffenseTeam,row.p3,'FUMBLE RECOVERY TD', 1])
    return pd.DataFrame(new_rows, columns = ['Game', 'Team', 'Player', 'Play', 'Play_Value'])

def clean_pass(row):
    Game = row.GameDate+row.OffenseTeam+row.DefenseTeam
    new_rows = []
    if row.IsInterception == '1':
        new_rows.append([Game, row.DefenseTeam, row.DefenseTeam, 'INTERCEPTION', 1])
        if row.IsTouchdown=='1':
            new_rows.append([Game, row.DefenseTeam, row.DefenseTeam, 'INTERCEPTION TOUCHDOWN', 1])
        new_rows.append([Game, row.OffenseTeam, row.p1, 'QB INTERCEPTION', 1])
    else:
        new_rows.append([Game, row.OffenseTeam, row.p1, 'QB PASS YARD', row.yards])
        new_rows.append([Game, row.OffenseTeam, row.p2, 'PASS YARD', row.yards])
        new_rows.append([Game, row.OffenseTeam, row.p2, 'RECEPTION', 1])
        if row.IsTouchdown == '1':
            new_rows.append([Game, row.OffenseTeam, row.p1,'QB TD',1])
            new_rows.append([Game, row.OffenseTeam, row.p2,'PASS TD',1])
            new_rows.append([Game,row.DefenseTeam,row.DefenseTeam,'POINT ALLOWED',1])
    return pd.DataFrame(new_rows, columns = ['Game', 'Team', 'Player', 'Play', 'Play_Value'])

def two_points(row):
    Game = row.GameDate+row.OffenseTeam+row.DefenseTeam
    new_rows = []
    if row.IsTwoPointConversionSuccessful == '1':
        new_rows.append([Game, row.OffenseTeam, row.p1, 'TWO POINT', 1])
        new_rows.append([Game, row.OffenseTeam, row.p2, 'TWO POINT', 1])
    return pd.DataFrame(new_rows, columns = ['Game', 'Team', 'Player', 'Play', 'Play_Value'])

def clean_kicks(row):
    Game = row.GameDate+row.OffenseTeam+row.DefenseTeam
    new_rows = []
    r=re.compile('NO GOOD')
    r2=re.compile('\d{1,2}')
    points = r.search(row.Description)
    if points != None:
        if row.PlayType == 'FIELD GOAL':
            yards=r2.findall(row.Description[2])
            new_rows.append([Game, row.OffenseTeam, row.p1, 'FG', yards])
        if row.PlayType == 'EXTRA POINT':
            new_rows.append([Game, row.OffenseTeam, row.p1, 'EXTRA POINT', 1])
    return pd.DataFrame(new_rows, columns = ['Game', 'Team', 'Player', 'Play', 'Play_Value'])


## Gets the 
def DKPoints(row):
    if row.Play=='PASS YARD' or row.Play=='RUSH YARDS':
        points=row.Play_Value*.1
        if row.Play_Value>100:
            points+=3
    elif row.Play=='RECEPTION':
        points=row.Play_Value
    elif row.Play=='FUMBLE':
        points=row.Play_Value*-1
    elif row.Play=='QB INTERCEPTION':
        points=row.Play_Value*-1    
    elif row.Play=='QB PASS YARD':
        points=row.Play_Value*.04
        if row.Play_Value>100:
            points+=3
    elif row.Play=='RUSH TD' or row.Play=='PASS TD' or row.Play=='QB TD' or row.Play=='INTERCEPTION TOUCHDOWN' or row.Play=='FUMBLE RECOVERY TD':
        points=row.Play_Value*6
    elif row.Play=='INTERCEPTION' or row.Play=='FUMBLE RECOVERY':
        points=row.Play_Value*2
    elif row.Play=='POINT ALLOWED':
        if row.Play_Value==0:
            points=10
        elif row.Play_Value<=6:
            points=7
        elif row.Play_Value<=13:
            points=4
        elif row.Play_Value<=20:
            points=1
        elif row.Play_Value<=27:
            points=0
        elif row.Play_Value<=34:
            points=-1
        else:
            points=-4
    else:
        points=0
    return points

def clean_name(player):
    p=player.split('-')
    if len(p)>1:
        return p[1].lower()
    else:
        return p[0].lower()

def clean_names2(row):
    if row['Position']!='DST':
        return row['n1'][0].lower()+'.'+row['n2'].lower()
    else:
        return(Inverse_Team_Map[row['Name'].strip()].lower())
    
def weighted_avg(x):
    if len(x)<=2:
        return np.mean(x)
    else:
        recent=x[-2:]
        past=x[:-2]
        wavg=((.5*np.mean(past))+np.mean(recent))/2
        return wavg
 
def football_etl(injured_players):
    """
    Takes an injured players list and produces a 'final' dataframe
    a CSV from draftkings with the salaries called DKSalaries.csv and football 
    play by play data from nflsavaant.com called pbp-2018.csv.
    """
    #import and clean play by play data
    football = etl.fromcsv('pbp-2018.csv')
    football = etl.select(football, lambda col: col.IsNoPlay=='0')
    football = etl.select(football, lambda col: col.OffenseTeam != '')
    football = etl.addfield(football,'players', lambda col: parse_description(col.Description))
    football = etl.unpack(football, 'players', ['p1', 'p2', 'p3','p4'])
    football = etl.addfield(football, 'yards', lambda col: get_yards(col.Description))
    football = etl.cut(football, ['GameDate', 'OffenseTeam'
                                  ,'DefenseTeam','p1','p2','p3','p4','Description','PlayType','IsTouchdown','IsSack'
                                  , 'IsInterception', 'IsFumble', 'IsTwoPointConversionSuccessful', 'IsIncomplete'
                                  , 'yards'])
    clean = etl.todataframe(football)   
    play_points=pd.DataFrame(columns=['Game', 'Team', 'Player', 'Play','Play_Value', 'GameDate'])
    for index, row in clean.iterrows():
        if row.PlayType == 'RUSH':
            play_points=pd.concat([play_points,clean_rush(row)], ignore_index=True, sort=False)
        if row.IsFumble == '1':
            play_points=pd.concat([play_points,fumble(row)], ignore_index=True, sort=False)
        if row.IsIncomplete == '0' and row.PlayType=='PASS':
            play_points=pd.concat([play_points,clean_pass(row)], ignore_index=True, sort=False)
        if row.PlayType=='TWO-POINT CONVERSION':
            play_points=pd.concat([play_points,two_points(row)], ignore_index=True, sort=False)
        if row.PlayType=='FIELD GOAL' or row.PlayType=='EXTRA POINT':
            play_points=pd.concat([play_points,clean_kicks(row)], ignore_index=True, sort=False)
    points=play_points.groupby(['Game','Player','Team','Play'], as_index=False)[['Play_Value']].sum()
    points['dk_points']=points.apply(lambda row: DKPoints(row),axis=1)
    points_by_game=points.groupby(['Game','Player','Team'], as_index=False)[['dk_points']].sum()
    points_by_game['Clean Name']=points_by_game.apply(lambda row: clean_name(row['Player']), axis=1)
    points_by_game=points_by_game.sort_values('Game', ascending=True)
    points_by_player=points_by_game.groupby(['Clean Name'], as_index=False).agg({'dk_points':[np.mean, np.var, lambda x: weighted_avg(x)]})
    points_by_player.columns=['key', 'Avg Points', 'Point Variance', 'Weighted Average']
    
    #import and clean draftkings salary csv
    salaries=etl.fromcsv('DKSalaries.csv')
    salaries=etl.addfield(salaries, 'names',lambda row: row['Name'].split(" "))
    salaries=etl.unpack(salaries, 'names', ['n1', 'n2', 'n3'])
    salaries=etl.addfield(salaries, 'key', lambda row: clean_names2(row))
    salary=etl.todataframe(salaries)
    
    final=pd.merge(points_by_player, salary, left_on='key', right_on='key')
    final=final[['key', 'Avg Points', 'Point Variance', 'Position', 'Salary', 'TeamAbbrev','AvgPointsPerGame','Weighted Average']]
    final.columns=['Name', 'Avg Points', 'Point Variance', 'Position', 'Salary', 'Team','DK Avg Points','Weighted Average']
    final['Salary']=final['Salary'].astype(int)
    for i in injured_players:
        final=final[final['Name']!=i]
    final=final.dropna()
    final=final.reset_index()
    return final