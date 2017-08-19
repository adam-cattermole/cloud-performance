data.azure = full.output[full.output$provider=='azure', names(full.output) != 'provider']
data.aws = full.output[full.output$provider=='aws', names(full.output) != 'provider']
data.azure = droplevels(data.azure)
data.aws = droplevels(data.aws)
