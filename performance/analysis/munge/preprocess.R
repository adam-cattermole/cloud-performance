data.azure = full.output[full.output$provider=='azure', names(full.output) != 'provider'] %>%
  mutate(overall=gm.rowmeans(.[,4:14]))
data.aws = full.output[full.output$provider=='aws', names(full.output) != 'provider'] %>%
  mutate(overall=gm.rowmeans(.[,4:14]))
data.azure = droplevels(data.azure)
data.aws = droplevels(data.aws)
