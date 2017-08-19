library(ProjectTemplate)
load.project()

### AVERAGE DATA FRAMES ###

data.average.azure = data.azure %>%
  mutate(overall=gm.rowmeans(.[,4:14])) %>%
  group_by(vm_type, vm_size) %>%
  summarise_each(funs(mean), -iteration)

data.average.azure

data.average.aws = data.aws %>%
  mutate(overall=gm.rowmeans(.[,4:14])) %>%
  group_by(vm_type, vm_size) %>%
  summarise_each(funs(mean), -iteration)

data.average.aws

### SPECS ###

azure.specs %>% tbl_df()
aws.specs %>% tbl_df()


# TODO: ATTEMPT TO RECREATE PAPER GRAPHS WITH MORE CLARITY
