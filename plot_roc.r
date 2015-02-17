loadme <- function (name) {
    a <- read.table(name, sep="")
    colnames(a) <- c('thresh', 'gay->gay', 'gay->str', 'gayu', 'str->gay', 'str->str','stru','accuracy', 'f', 'prec', 'rec', 'tpr', 'fpr')
    return (a)
}


lp <- read.table('FPR_TPR_Precision.txt', sep="", header=TRUE)
colnames(lp) <- c('fpr', 'tpr', 'prec')

names <- c('clique_graph/02-2015_clique_graph.cont', 'clique_graph/02-2015_clique_graph_removed_chunks.cont')
results <- lapply (names, loadme)

pdf("roc.pdf")
linetype <- c(1:length(results)+1)
colors <- rainbow(length(results)+1)

plot(c(0,1), c(0,1), type="n", xlab="False Positive Rate", ylab = "True Positive Rate")
lines(c(0,1), c(0,1))
for (i in 1:length(results)) {
    lines(results[[i]]$fpr, results[[i]]$tpr, type="b", lwd=1.5, lty=linetype[i], col=colors[i])
}

plotchar <- c('all', 'removed')




legend(.7,.95, plotchar, cex=0.8, col=colors, lty=linetype, title="Algorithm")

