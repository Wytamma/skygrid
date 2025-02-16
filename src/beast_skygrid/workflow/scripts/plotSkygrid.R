library(dplyr)
library(ggplot2)
library(skyplotr)
library(optparse)

# Set up the command line argument parser
option_list <- list(
    make_option(c("-i", "--input"),
        type = "character", default = NULL,
        help = "Path to the BEAST log file",
        metavar = "file"
    ),
    make_option(c("-d", "--mrsd"),
        type = "character",
        help = "Age of youngest tip (decimal year)", metavar = "numeric"
    ),
    make_option(c("-o", "--output"),
        type = "character",
        help = "Path to the output file",
        metavar = "file"
    ),
    make_option(c("-b", "--burnin"),
        type = "numeric", default = 0.1,
        help = "Proportion of samples to discard as burnin",
        metavar = "numeric"
    )

)

# Parse command line arguments
opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)
print(opt)
samples <- read.csv(opt$input, sep = "\t", header = TRUE, comment.char = "#")

# Burnin 10%
burnin <- round(nrow(samples) * opt$burnin)
samples <- samples[-(1:burnin), ]

root_height <- samples$treeModel.rootHeight
log_pop_size <- select(samples, starts_with("skygrid.logPopSize"))
cutoff <- samples$skygrid.cutOff[1]
skygrid <- prepare_skygrid(
    root_height, log_pop_size, cutoff, age_of_youngest=as.numeric(opt$mrsd))
# discard last row
skygrid <- skygrid[-nrow(skygrid), ]

skygrid <- mutate(
  skygrid,
  across(
    .cols = all_of(c("trajectory", "trajectory_low", "trajectory_high")),
    .fns = exp
  )
)


plot_title <- ggtitle("Population size trajectory",
                      "with median and 95% intervals")

g <- skyplot(skygrid, fill="darkcyan") + plot_title + ylab("Effective population size") + xlab(NULL)

# Save the plot svg
ggsave(paste0(opt$output, ".svg"), width = 6, height = 4)

# Save the plot as a pdf
ggsave(paste0(opt$output, ".pdf"), width = 6, height = 4)

# Save the plot as a png
ggsave(paste0(opt$output, ".png"), width = 6, height = 4)
