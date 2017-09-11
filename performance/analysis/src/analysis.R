# TODO: ATTEMPT TO RECREATE PAPER GRAPHS WITH MORE CLARITY #

#### AZURE: Initial Reproduction of Graphics ####

## Separate by VM type

## BASIC ##
data.azure.basic = data.azure %>%
  filter(as.character(vm_type) == "basic")

# average
data.average.azure.basic = data.azure.basic %>%
  group_by(vm_size) %>%
  summarise_each(funs(mean), -c(iteration,vm_type)) 
colnames(data.average.azure.basic) = col.headers[-1]

# output
data.average.azure.basic
write.csv(format(data.average.azure.basic, digits=3, nsmall=2), file = "data/output/data_average_azure_basic.csv", quote = FALSE, row.names = FALSE)

## STANDARD ##

data.azure.standard = data.azure %>%
  filter(as.character(vm_type) == "standard" & !endsWith(as.character(vm_size), "v2"))

# average
data.average.azure.standard = data.azure.standard %>%
  group_by(vm_size) %>%
  summarise_each(funs(mean), -c(iteration,vm_type))
colnames(data.average.azure.standard) = col.headers[-1]

# output
data.average.azure.standard
write.csv(format(data.average.azure.standard, digits=3, nsmall=2), file = "data/output/data_average_azure_standard.csv", quote = FALSE, row.names = FALSE)
  
## STANDARD V2 ##

data.azure.standard.v2 = data.azure %>%
  filter(as.character(vm_type) == "standard" & endsWith(as.character(vm_size), "v2"))

# averaage
data.average.azure.standard.v2 = data.azure.standard.v2 %>%
  group_by(vm_size) %>%
  summarise_each(funs(mean), -c(iteration,vm_type)) %>%
  mutate(vm_size = factor(gsub("_"," ",vm_size), levels=gsub("_", " ",levels(vm_size))))
colnames(data.average.azure.standard.v2) = col.headers[-1]


# output
data.average.azure.standard.v2
write.csv(format(data.average.azure.standard.v2, digits=3, nsmall=2), file = "data/output/data_average_azure_standard_v2.csv", quote = FALSE, row.names = FALSE)

## Graphs

#test combination
# test = rbind(data.azure.basic, data.azure.standard)
# ggplotSummaryAzure(merge(test, azure.specs), title="Test")

ggplotSummaryAzure(merge(data.azure.basic, azure.specs), title="Performance of Azure 'Basic' Instance Types")
ggsave("data_azure_basic.png", device="png", path="graphs/", width = 200, height = 180, units="mm")
ggplotSummaryAzure(merge(data.azure.standard, azure.specs), title="Performance of Azure 'Standard' Instance Types")
ggsave("data_azure_standard.png", device="png", path="graphs/", width = 200, height = 180, units="mm")
ggplotSummaryAzure(merge(data.azure.standard.v2, azure.specs), title="Performance of Azure 'Standard V2' Instance Types")
ggsave("data_azure_standard_v2.png", device="png", path="graphs/", width = 200, height = 180, units="mm")


#### EC2: Initial Reproduction of Graphics ####

## Separate by VM type

## T2 ##

data.aws.t2 = data.aws %>%
  filter(as.character(vm_type) == "t2")

data.aws.t2

## M4 ##

data.aws.m4 = data.aws %>%
  filter(as.character(vm_type) == "m4")

data.aws.m4

## C4 ##

data.aws.c4 = data.aws %>%
  filter(as.character(vm_type) == "c4")

data.aws.c4

## Graphs

ggplotSummaryAws(merge(data.aws.t2, aws.specs), title="Performance of AWS t2 Instance Types")
ggsave("data_aws_t2.png", device="png", path="graphs/", width = 200, height = 180, units="mm")
ggplotSummaryAws(merge(data.aws.m4, aws.specs), title="Performance of AWS m4 Instance Types")
ggsave("data_aws_m4.png", device="png", path="graphs/", width = 200, height = 180, units="mm")
ggplotSummaryAws(merge(data.aws.c4, aws.specs), title="Performance of AWS c4 Instance Types")
ggsave("data_aws_c4.png", device="png", path="graphs/", width = 200, height = 180, units="mm")

data.aws


#### BOTH: Create a chart with both Azure and AWS averages ####

## Average data frames

## Azure average ##

data.average.azure = data.azure %>%
  group_by(vm_type, vm_size) %>%
  summarise_each(funs(mean), -iteration)
colnames(data.average.azure) = col.headers

data.average.azure
write.csv(format(data.average.azure, digits=3, nsmall=2), file = "data/output/data_average_azure.csv", quote = FALSE, row.names = FALSE)

## AWS average ##

data.average.aws = data.aws %>%
  group_by(vm_type, vm_size) %>%
  summarise_each(funs(mean), -iteration)
colnames(data.average.aws) = col.headers

data.average.aws
write.csv(format(data.average.aws, digits=3, nsmall=2), file = "data/output/data_average_aws.csv", quote = FALSE, row.names = FALSE)

## Combine to contain both

data.average.azure.merge = merge(data.average.azure, azure.specs) %>%
  mutate(provider = "Azure") %>%
  select(provider, overall, cost)

data.average.aws.merge = merge(data.average.aws, aws.specs) %>%
  mutate(provider = "AWS") %>%
  select(provider, overall, cost)

data.average.merged = rbind(data.average.azure.merge, data.average.aws.merge)

## Graph

ggplot(data.average.merged, aes(x=cost, y=overall, colour=provider)) +
  geom_point() +
  scale_x_continuous(breaks = seq(0,0.8,0.1), limits = c(0,0.8)) +
  scale_y_continuous(breaks = seq(0,300,25), limits = c(0,300)) +
  theme_bw() +
  scale_colour_brewer(palette = "Set1") +
  labs(title="Average Performance of All Instances for Both Providers",
       x="Cost ($/hour)",
       y="Overall Performance Averages",
       colour="Provider") +
  theme(plot.title = element_text(size=16,hjust = 0.5, margin = margin(t = 10, b = 10)),
        axis.text = element_text(size=12),
        axis.title = element_text(size=14),
        axis.title.x = element_text(margin = margin(t = 10, b = 10)),
        axis.title.y = element_text(margin = margin(l = 10, r = 10)),
        legend.text = element_text(size=12),
        legend.title = element_text(size=14))
ggsave("data_both.png", device="png", path="graphs/", width = 200, height = 180, units="mm")


#### Azure: Single Thread ####

data.average.azure.single.thread = data.azure.single.thread %>%
  group_by(vm_size) %>%
  summarise_each(funs(mean), -c(vm_type, iteration)) %>%
  mutate(vm_size = factor(gsub("_"," ",vm_size), levels=gsub("_", " ",levels(vm_size))))
colnames(data.average.azure.single.thread) = col.headers[-1]

data.average.azure.single.thread
write.csv(format(data.average.azure.single.thread, digits=3, nsmall=2), file = "data/output/data_average_azure_single_thread.csv", quote = FALSE, row.names = FALSE)

merge(data.azure.single.thread, azure.specs)
ggplotSummaryAzure(merge(data.azure.single.thread, azure.specs), title="", yinterval = 20)
ggsave("data_azure_single_thread.png", device="png", path="graphs/", width = 200, height = 180, units="mm")


### Write specification tables ###

spec.header = c("VM Type", "VM Size", "Cores", "Memory GB", "Cost $/hour")

## azure ##
azure.specs.print = azure.specs %>%
  mutate(vm_size = factor(gsub("_"," ",vm_size), levels=gsub("_", " ",levels(vm_size))))
colnames(azure.specs.print) = spec.header
write.csv(format(azure.specs.print, digits=3, nsmall=2), file = "data/output/data_azure_specs.csv", quote = FALSE, row.names = FALSE)

## aws ##

aws.specs.print = aws.specs
colnames(aws.specs.print) = spec.header
write.csv(format(aws.specs.print, digits=3, nsmall=2), file = "data/output/data_aws_specs.csv", quote = FALSE, row.names = FALSE)