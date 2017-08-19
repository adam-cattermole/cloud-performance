# Function for geometric mean
gm.mean = function(x, na.rm=TRUE) {
  exp(sum(log(x[x > 0]), na.rm=na.rm) / length(x))
}

# Applies geometric mean across rows
gm.rowmeans = function(x) {
  apply(x, 1, gm.mean)
}