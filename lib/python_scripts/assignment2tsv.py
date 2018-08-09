import sys

def read_uc(uc_filename):
	annotations = {}
	# headers: ['type', 'idx', 'length', 'similarity', 'orientation', 'nuy1', 'nuy2', 'compact', 'name', 'hit']

	with open(uc_filename) as fp:
		for line in fp:
			type, _, _, similarity, _, _, _, _, name, hit = line.strip().split("\t")

			if not name in annotations:
				annotations[name] = []

			if type != "N":
				annotations[name].append({
					"similarity": (float(similarity) / 100.0),
					"sequence_id": hit[:hit.find(' ')],
					"taxon": hit[hit.find(' ')+1:]
				})

	return annotations



def to_tsv(uc_filename, outfile, consensus_threshold):
	annotations = read_uc(uc_filename)

	print("Write in {}".format(outfile))

	with open(outfile, "w") as fw:
		# Write the header
		fw.write("sequence\ttaxon\tmean similarity\treference ids\n")

		# List all the annotations
		for id, annotation in annotations.items():
			# Make a consensus taxonomy
			cons = consensus(annotation, consensus_threshold)
			# Write the outfile
			fw.write("{}\t{}\t{}\t{}\n".format(id, cons["taxon"], cons["identity"], ";".join(cons["ids"])));



def consensus (taxa, threshold):
	if len(taxa) == 0:
		return {"taxon":"unassigned", "identity":0, "ids":[]}

	used_taxa = taxa
	max_sim = 0

	# Taxa filtering with direct acceptance
	for taxon in taxa:
		# Over the direct acceptance threshold
		if taxon["similarity"] >= threshold:
			# First to be over the threshold
			if max_sim < taxon["similarity"]:
				max_sim = taxon["similarity"]
				used_taxa = [taxon]
			# Equals the maximum
			elif taxon["similarity"] == max_sim:
				used_taxa.append(taxon)


	# Create consensus taxonomy
	detailed_taxa = [taxon["taxon"].split(";") for taxon in used_taxa]
	mean = sum([float(taxon["similarity"]) for taxon in used_taxa]) / len(used_taxa)
	ids = [taxon["sequence_id"] for taxon in used_taxa]

	# Taxo consensus
	cons = used_taxa[0]["taxon"]
	if len(used_taxa) != 1:
		cons = taxo_consensus (detailed_taxa)

	return {"taxon": cons, "identity": mean, "ids": ids}


def taxo_consensus (detailed_taxa):
	cons = '';
	tax_id = 0;
	while tax_id < len(detailed_taxa[0]):
		# Reference taxon
		taxon = detailed_taxa[0][tax_id]
		for idx in range(1, len(detailed_taxa)):
			# Verify the taxon for each assignment
			if taxon != detailed_taxa[idx][tax_id]:
				return cons[1:]

		if ((not taxon) or taxon == ''):
			break

		cons += ';' + taxon
		tax_id += 1

	return cons[1:]




if "__main__" == __name__:
	# Arguments parsing
	function = None
	uc_filename = ""
	consensus_threshold = 0
	outfile = ""

	for idx in range(len(sys.argv)):
		if sys.argv[idx] == '-tsv_out':
			function = to_tsv
			outfile = sys.argv[idx+1]
			idx += 1
		elif sys.argv[idx] == "-uc":
			uc_filename = sys.argv[idx+1]
			idx += 1
		elif sys.argv[idx] == "-threshold":
			consensus_threshold = float(sys.argv[idx+1])
			idx += 1

	function(uc_filename, outfile, consensus_threshold)
	exit(0)