use Getopt::Std;
use File::Find;

my (%opts,@files,$listfile,$database);

getopts('vlrf:i:',\%opts);
if (($#ARGV>=0) && (-d $ARGV[0])) {
	chdir($ARGV[0]) or die("chdir error");
}
$listfile=$opts{'i'} || 'cscope.files';
$database=$opts{'f'} || 'cscope.out';
if ($opts{'v'}) {
	print "Creating list of files to index ...\n";
}
find(\&wanted,'.');
open(FH,">$listfile");
print FH join("\n",@files);
close(FH);
if ($opts{'v'}) {
	print "Creating list of files to index ... done\n";
}
if ($opts{'l'}) {
	exit(0);
}
if ($opts{'v'}) {
	print "Indexing files ...\n";
}
system("cscope -b -i $listfile -f $database");
if ($opts{'v'}) {
	print "Indexing files ... done\n";
}

sub wanted {
	if (/\.([chly](xx|pp)*|cc|hh)$/) {
		my $fpath=$File::Find::name;
		unless ($fpath=~m#[/\\]CSV[/\\]#) {
			push @files,$fpath;
		}
	}
}
