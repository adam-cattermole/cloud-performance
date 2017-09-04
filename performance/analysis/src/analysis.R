library(ProjectTemplate)
load.project()

### AVERAGE DATA FRAMES ###

data.average.azure = data.azure %>%
  group_by(vm_type, vm_size) %>%
  summarise_each(funs(mean), -iteration)

data.average.azure

data.average.aws = data.aws %>%
  group_by(vm_type, vm_size) %>%
  summarise_each(funs(mean), -iteration)

data.average.aws

### SPECS ###

azure.specs %>% tbl_df()
aws.specs %>% tbl_df()


# TODO: ATTEMPT TO RECREATE PAPER GRAPHS WITH MORE CLARITY


#### AZURE: Initial Reproduction of Graphics ####

data.azure.basic = data.azure %>%
  filter(as.character(vm_type) == "basic")

data.azure.basic

data.azure.standard = data.azure %>%
  filter(as.character(vm_type) == "standard" & !endsWith(as.character(vm_size), "v2"))

data.azure.standard
  
data.azure.standard.v2 = data.azure %>%
  filter(as.character(vm_type) == "standard" & endsWith(as.character(vm_size), "v2"))

data.azure.standard.v2


ggplotSummaryCi(merge(data.azure.basic, azure.specs), title="Performance of Azure 'Basic' Instance Types")
ggplotSummaryCi(merge(data.azure.standard, azure.specs), title="Performance of Azure 'Standard' Instance Types")
ggplotSummaryCi(merge(data.azure.standard.v2, azure.specs), title="Performance of Azure 'Standard V2' Instance Types")


#### EC2: Initial Reproduction of Graphics ####

data.aws.t2 = data.aws %>%
  filter(as.character(vm_type) == "t2")

data.aws.t2

data.aws.m4 = data.aws %>%
  filter(as.character(vm_type) == "m4")

data.aws.m4

data.aws.c4 = data.aws %>%
  filter(as.character(vm_type) == "c4")

data.aws.c4

## This sort of works, see summary.R in functions. The scaling is slightly off

ggplotSummaryCi(merge(data.aws.t2, aws.specs), title="Performance of AWS t2 Instance Types")



