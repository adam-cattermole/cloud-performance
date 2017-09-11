summarySE <- function(data=NULL, measurevar, groupvars=NULL, na.rm=FALSE,
                      conf.interval=.95, .drop=TRUE) {
  
  # New version of length which can handle NA's: if na.rm==T, don't count them
  length2 <- function (x, na.rm=FALSE) {
    if (na.rm) sum(!is.na(x))
    else       length(x)
  }
  
  # This does the summary. For each group's data frame, return a vector with
  # N, mean, and sd
  datac <- ddply(data, groupvars, .drop=.drop,
                 .fun = function(xx, col) {
                   c(N    = length2(xx[[col]], na.rm=na.rm),
                     mean = mean   (xx[[col]], na.rm=na.rm),
                     sd   = sd     (xx[[col]], na.rm=na.rm)
                   )
                 },
                 measurevar
  )
  
  # Rename the "mean" column    
  datac <- plyr::rename(datac, c("mean" = "overall"))
  
  datac$se <- datac$sd / sqrt(datac$N)  # Calculate standard error of the mean
  
  # Confidence interval multiplier for standard error
  # Calculate t-statistic for confidence interval: 
  # e.g., if conf.interval is .95, use .975 (above/below), and use df=N-1
  ciMult <- qt(conf.interval/2 + .5, datac$N-1)
  datac$ci <- datac$se * ciMult
  
  return(datac)
}

# Uses function above to plot with 95% conifdence intervals
ggplotSummaryCi = function(summary, measurevar="overall", xvalue="cost", groupvar=c("vm_type","vm_size","cost"), label=c("Cost ($/hour)", "Overall Performance"), title=NULL, xinterval, yinterval) {
  pd = position_dodge(0.1)
  pos = which.max(summary[[measurevar]])
  # This logic isn't great - a lower "overall" value could end up with a massive out of bounds ci
  yscale = ceiling((summary[pos,measurevar]+summary[pos,"ci"])/yinterval)*yinterval
  xscale = ceiling(max(summary[[xvalue]]/xinterval))*xinterval
  # plot
  ggplot(summary, aes_string(x=xvalue,y=measurevar, colour="vm_size")) +
    geom_errorbar(aes(ymin=summary[[measurevar]]-ci, ymax=summary[[measurevar]]+ci), width=xscale/50, position=pd) +
    suppressMessages(geom_point(position=pd)) +
    scale_x_continuous(breaks=seq(0,xscale,max(c(round((xscale/0.4))*0.05,0.05))), limits=c(0,xscale)) +
    scale_y_continuous(breaks=seq(0,yscale,round((yscale/10)/5)*5),limits=c(0,yscale)) +
    theme_bw() +
    scale_colour_brewer(palette = "Set1") +
    labs(title=title,
         x=label[1],
         y=label[2],
         colour="VM Size") +
    theme(plot.title = element_text(size=16,hjust = 0.5, margin = margin(t = 10, b = 10)),
          axis.text = element_text(size=12),
          axis.title = element_text(size=14),
          axis.title.x = element_text(margin = margin(t = 10, b = 10)),
          axis.title.y = element_text(margin = margin(l = 10, r = 10)),
          legend.text = element_text(size=12),
          legend.title = element_text(size=14))
}


## TODO: Separate out a caller for azure and ec2 just to change the scaling of the axes


ggplotSummaryAzure = function(data, measurevar="overall", xvalue="cost", groupvar=c("vm_type","vm_size","cost"), label=c("Cost ($/hour)", "Overall Performance"), title=NULL, xinterval = 0.1, yinterval = 50) {
  s = summarySE(data, measurevar, groupvar) %>%
    mutate(vm_size = factor(toupper(gsub("_"," ",vm_size)), levels=toupper(gsub("_"," ",azure.order))))
  print(s)
  ggplotSummaryCi(s, measurevar, xvalue, groupvar, label, title, xinterval = xinterval, yinterval = yinterval)
}

ggplotSummaryAws = function(data, measurevar="overall", xvalue="cost", groupvar=c("vm_type","vm_size","cost"), label=c("Cost ($/hour)", "Overall Performance"), title=NULL, xinterval = 0.05, yinterval=20) {
  s = summarySE(data, measurevar, groupvar)
  print(s)
  ggplotSummaryCi(s, measurevar, xvalue, groupvar, label, title, xinterval = xinterval, yinterval = yinterval)
}

# plotSettings = function(title, label) {
#   return(c(
#   theme_bw(),
#   scale_colour_brewer(palette = "Set1"),
#   labs(title=title,
#        x=label[1],
#        y=label[2],
#        colour="VM Size"),
#   theme(plot.title = element_text(size=16,hjust = 0.5, margin = margin(t = 10, b = 10)),
#         axis.text = element_text(size=12),
#         axis.title = element_text(size=14),
#         axis.title.x = element_text(margin = margin(t = 10, b = 10)),
#         axis.title.y = element_text(margin = margin(l = 10, r = 10)),
#         legend.text = element_text(size=12),
#         legend.title = element_text(size=14))))
# }