# TODO: ATTEMPT TO RECREATE PAPER GRAPHS WITH MORE CLARITY #

#### AZURE: Initial Reproduction of Graphics ####

## Separate by VM type

data.azure.basic = data.azure %>%
  filter(as.character(vm_type) == "basic")

data.azure.basic

data.azure.standard = data.azure %>%
  filter(as.character(vm_type) == "standard" & !endsWith(as.character(vm_size), "v2"))

data.azure.standard
  
data.azure.standard.v2 = data.azure %>%
  filter(as.character(vm_type) == "standard" & endsWith(as.character(vm_size), "v2"))

data.azure.standard.v2

## Graphs

#test combination
# test = rbind(data.azure.basic, data.azure.standard)
# ggplotSummaryAzure(merge(test, azure.specs), title="Test")

ggplotSummaryAzure(merge(data.azure.basic, azure.specs), title="Performance of Azure 'Basic' Instance Types")
ggplotSummaryAzure(merge(data.azure.standard, azure.specs), title="Performance of Azure 'Standard' Instance Types")
ggplotSummaryAzure(merge(data.azure.standard.v2, azure.specs), title="Performance of Azure 'Standard V2' Instance Types")


#### EC2: Initial Reproduction of Graphics ####

## Separate by VM type

data.aws.t2 = data.aws %>%
  filter(as.character(vm_type) == "t2")

data.aws.t2

data.aws.m4 = data.aws %>%
  filter(as.character(vm_type) == "m4")

data.aws.m4

data.aws.c4 = data.aws %>%
  filter(as.character(vm_type) == "c4")

data.aws.c4

## Graphs

ggplotSummaryAws(merge(data.aws.t2, aws.specs), title="Performance of AWS t2 Instance Types")
ggplotSummaryAws(merge(data.aws.m4, aws.specs), title="Performance of AWS t2 Instance Types")
ggplotSummaryAws(merge(data.aws.c4, aws.specs), title="Performance of AWS t2 Instance Types")


#### BOTH: Create a chart with both Azure and AWS averages ####

## Average data frames

data.average.azure = data.azure %>%
  group_by(vm_type, vm_size) %>%
  summarise_each(funs(mean), -iteration)

data.average.azure

data.average.aws = data.aws %>%
  group_by(vm_type, vm_size) %>%
  summarise_each(funs(mean), -iteration)

data.average.aws

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
  scale_x_continuous(breaks = seq(0,0.8,0.05), limits = c(0,0.8)) +
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


#### Azure: Single Thread ####

ggplotSummaryAzure(merge(data.azure.single.thread, azure.specs), title="", yinterval = 20)
