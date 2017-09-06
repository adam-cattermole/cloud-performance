data.azure = full.output %>%
  filter(provider == "azure") %>%
  select(-provider) %>%
  mutate(overall=gm.rowmeans(.[,4:14]))

data.aws = full.output %>%
  filter(provider == "aws") %>%
  select(-provider) %>%
  mutate(overall=gm.rowmeans(.[,4:14])) %>%
  mutate(vm_size = factor(vm_size, levels=c("micro", "small", "medium", "large", "xlarge", "2xlarge")))

data.azure = droplevels(data.azure)
data.aws = droplevels(data.aws)

data.azure.single.thread = azure.single.thread %>%
  select(-provider) %>%
  mutate(overall=gm.rowmeans(.[,4:14]))
