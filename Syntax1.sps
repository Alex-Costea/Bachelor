* Encoding: UTF-8.
 GET FILE = 'C:\Users\12590126\OneDrive - UvA\Desktop\data.sav'.
EXECUTE.

*filter.
descriptives in_centrality out_centrality retweets_normalized
/save.

USE ALL.
COMPUTE filter_1=(Zretweets_normalized < 3.29 AND Zin_centrality <3.29 AND Zout_centrality <3.29).
FORMATS filter_1 (f1.0).
FILTER BY filter_1.
EXECUTE.

*descriptives

DESCRIPTIVES VARIABLES=keywords retweets tweets in_centrality out_centrality
  /STATISTICS=MEAN STDDEV MIN MAX.

*Regression 1.
GRAPH
  /SCATTERPLOT(BIVAR)=in_centrality WITH retweets_normalized
  /MISSING=LISTWISE.

REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT retweets_normalized
  /METHOD=ENTER in_centrality.

*Regression 2.
GRAPH
  /SCATTERPLOT(BIVAR)=out_centrality WITH retweets_normalized
  /MISSING=LISTWISE.

REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT retweets_normalized
  /METHOD=ENTER out_centrality.

*Regression 3.
COMPUTE retweets_unconfounded=retweets_normalized-(7564.727668+576250.378235*in_centrality).
EXECUTE.

GRAPH
  /SCATTERPLOT(BIVAR)=out_centrality WITH retweets_unconfounded
  /MISSING=LISTWISE.


REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT retweets_normalized
  /METHOD=ENTER in_centrality out_centrality.

REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT retweets_unconfounded
  /METHOD=ENTER out_centrality.
