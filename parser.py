#!/usr/bin/env python3
# -*- coding: utf_8 -*-

"""
Example of recursive descent parser written by hand using plex module as scanner
NOTE: This progam is a language recognizer only.
Grammar :


Stmt_list       ->      Stmt Stmt_list | ε
Stmt            ->      id = Expr | print Expr
Expr            ->      Term Term_tail
Term_tail       ->      ORop Term Term_tail | ε
Term            ->      Factor Factor_tail
Factor_tail     ->      ANDop Factor Factor_tail |ε
Factor          ->      Statmnt Statmnt_tail
Statmnt         ->      NOTop |ε
Statmnt_tail    ->      (Expr) | id | bool_value
ORop            ->      OR
ANDop           ->      AND
NOTop           ->      NOT


print: το keyword 'print'
id: όνομα μεταβλητής
bool_value:  true, false, t, f, 0 και 1

B)                
                        FirstSETs                      FollowSETs
Stmt_list       ->      id, print, ε                   #                                
Stmt            ->      id, print                                          id, print,#
Expr            ->      NOT, (, id, bool_value         ),id, print,#
Term_tail       ->      OR, ε                          ),id, print,#
Term            ->      NOT, (, id, bool_value         OR,) ,id , print,#
Factor_tail     ->      AND, ε                         OR,) ,id , print,#
Factor          ->      NOT, (, id, bool_value         AND, OR,) ,id , print,#
Statmnt         ->      NOT, ε                         (, id, bool_value
Statmnt_tail    ->      (, id, bool_value              AND, OR,) ,id , print,#
ORop            ->      OR                             NOT, (, id, bool_value
ANDop           ->      AND                            NOT, (, id, bool_value
NOTop           ->      NOT                            (, id, bool_value


  
"""


import plex



class ParseError(Exception):
        """ A user defined exception class, to describe parse errors. """
        pass



class MyParser:
        """ A class encapsulating all parsing functionality
        for a particular grammar. """
        
        def create_scanner(self,fp):
                """ Creates a plex scanner for a particular grammar 
                to operate on file object fp. """

                # define some pattern constructs
                letter = plex.Range("AZaz")
                digit = plex.Range("09")

                id = plex.Rep1(letter | digit)
                operator = plex.Any("!?()=#")             
                space = plex.Any(" \t\n")

                # the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
                lexicon = plex.Lexicon([
                        (operator,plex.TEXT),
                        (space,plex.IGNORE),
                        (id, 'id')
                        ])
                
                # create and store the scanner object
                self.scanner = plex.Scanner(lexicon,fp)
                
                # get initial lookahead
                self.la,self.val = self.next_token()


        def next_token(self):
                """ Returns tuple (next_token,matched-text). """
                
                return self.scanner.read()              

        
        def position(self):
                """ Utility function that returns position in text in case of errors.
                Here it simply returns the scanner position. """
                
                return self.scanner.position()
        

        def match(self,token):
                """ Consumes (matches with current lookahead) an expected token.
                Raises ParseError if anything else is found. Acquires new lookahead. """ 
                
                if self.la==token:
                        self.la,self.val = self.next_token()
                else:
                        raise ParseError("found {} instead of {}".format(self.la,token))
        
        
        def parse(self,fp):
                """ Creates scanner for input file object fp and calls the parse logic code. """
                
                # create the plex scanner for fp
                self.create_scanner(fp)
                
                # call parsing logic
                self.Stmt_list()
        
                        
        def Stmt_list(self):
                """ Stmt_list  ->  Stmt Stmt_list | ε """
                
                if self.la=='id' or self.la=='print':
                        self.Stmt()
                elif self.la=='#':    # from FOLLOW set!
                        return  
                else:
                        raise ParseError("in Stmt_list: id, print or # expected")
                                
        
        def Stmt(self):
                """ Stmt -> id = Expr | print Expr """
                if self.la=='id' :
                        self.match('id')
                        self.match('=')
                        self.Expr()
                elif self.la=='print':
                        self.match('print ')
                        self.Expr()
                else:
                        raise ParseError("in Stmt: id or print expected")
        
        
        def Expr(self):
                """ Expr  ->  Term Term_tail  """
                
                if self.la=='NOT' or self.la=='(' or self.la=='id' or self.la=='true' or self.la=='false' or self.la=='t' or self.la=='f' or self.la=='0' or self.la=='1':
                        self.Term()
                        self.Term_tail()
                else:
                        raise ParseError("in Expr: NOT, (, id, bool_value is expected")
                                

        def Term_tail(self):
                """ Term_tail  -> ORop Term Term_tail | ε """
                
                if self.la=='OR':
                        self.ORop()
                        self.Term()
                        self.Term_tail()
                elif self.la==')' or self.la=='id' or self.la==' print' or self.la=='#':    # from FOLLOW set!
                        return  
                else:
                        raise ParseError("in Term_tail: OR, ) ,id, print,# is expected")

        def Term(self):
                """ Term  -> Factor Factor_tail """
                
                if self.la=='NOT' or self.la=='(' or self.la=='id' or self.la=='true' or self.la=='false' or self.la=='t' or self.la=='f' or self.la=='0' or self.la=='1':
                        self.Factor()
                        self.Factor_tail()
                else:
                        raise ParseError("in Term: NOT, (, id, bool_value is expected")

        def Factor_tail(self):
                """ Factor_tail  -> ANDop Factor Factor_tail |ε """
                if self.la=='AND':
                        self.ANDop()
                        self.Factor()
                        self.Factor_tail()
                elif self.la=='OR' or self.la==')' or self.la=='id' or self.la=='print' or self.la=='#' :
                        return
                else:
                        raise ParseError("in Factor_tail: AND, OR, ), id, print or # is expected")

        def Factor(self):
                """ Factor  -> Statmnt Statmnt_tail """
                if self.la=='NOT' or self.la=='(' or self.la=='id' or self.la=='true' or self.la=='false' or self.la=='t' or self.la=='f' or self.la=='0' or self.la=='1':
                        self.Statmnt()
                        self.Statmnt_tail()
                else:
                        raise ParseError("in Factor: NOT, (, id, bool_value is expected")

        def Statmnt(self):
                """ Statmnt  ->  NOTop |ε """
                if self.la=='NOT':
                        self.NOTop()
                elif self.la=='(' or self.la=='id' or self.la=='true' or self.la=='false' or self.la=='t' or self.la=='f' or self.la=='0' or self.la=='1' : # from FOLLOW set!
                        return
                else:
                        raise ParseError("in Statmnt: NOT, (, id, bool_value is expected")

        def Statmnt_tail(self):
                """ Statmnt_tail  -> (Expr) | id | bool_value """
                if self.la=='(':
                        self.match('(')
                        self.Expr()
                        self.match(')')
                elif self.la=='id' :
                        self.match('id')
                elif self.la=='true' :
                        self.match('true')
                elif self.la=='false' :
                        self.match('false')
                elif self.la=='t' :
                        self.match('t')
                elif self.la=='f' :
                        self.match('f')
                elif self.la=='0' :
                        self.match('0')
                elif self.la=='1' :
                        self.match('1')
                else:
                        raise ParseError("in Statmnt_tail: (Expr), id or bool_value is expected")

        def ORop(self):
                """ ORop -> OR """
                if self.la=='OR':
                        self.match('OR')
                else:
                        raise ParseError("in ORop: OR is expected")
        
        def ANDop(self):
                """ ANDop -> AND """
                if self.la=='AND':
                        self.match('AND')
                else:
                        raise ParseError("in ANDop: AND is expected")

        def NOTop(self):
                """ Statmnt  ->  NOTop |ε """
                if self.la=='NOT':
                        self.match('NOT')
                else:
                        raise ParseError("in NOTop: NOT is expected")
                
                        
                        
                        
                        


                        
# the main part of prog

# create the parser object
parser = MyParser()

# open file for parsing
with open("recursive-descent-parsing-bool.txt","r") as fp:

        # parse file
        try:
                parser.parse(fp)
        except plex.errors.PlexError:
                _,lineno,charno = parser.position()     
                print("Scanner Error: at line {} char {}".format(lineno,charno+1))
        except ParseError as perr:
                _,lineno,charno = parser.position()     
                print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))

