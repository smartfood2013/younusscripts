#!/usr/bin/perl
# ii, Interest Integrator
# Ron Hale-Evans, rwhe@ludism.org
# 2009-07-1

$nargs = $#ARGV + 1;
srand;
# You may need to adjust the following values.
# depending on your environment

$home = $ENV{HOME};
$obessions = "$home/obessions.txt";
$browser = "firefox";
# Usage information

if ($nargs > 2) 
{
    $two = "\"ii chimp hilarious-consequences\" googles both terms.";
    $one = "\"ii chimp\" googles \"chimp\" plus a random obsession.";
    $zero = "\"ii\" by itself googles two random obessions.";
    die "usage:\n$two\n$one\n$zero\n";
}
elsif ($nargs == 2) 
{
    $arg1 = $ARGV[0];
    $arg2 = $ARGV[1];
}
elsif ($nargs == 1) 
{
    $arg1 = $ARGV[0];
    $arg2 = random_obession();
}
else 
{
    $arg1 = random_obession();
    $arg2 = random_obession();
}
$arg1 = munge($arg1);
$arg2 = munge($arg2);
$url = "http://www.google.com/search?num=100&q=$arg1+$arg2";

print "$url\n";
`$browser '$url'`;
sub random_obession()
{
   open FILE, "<$obessions" or die "Could not open obessions.txt :$!\n";
   rand($.) <1 and ($line=$_) while <FILE>;
   close FILE;
   return($line);
}
#tweek search terms so that they can form part of valid URL
sub munge($)
{
     my ($a) = @_;
     chomp($a);
     $a =~ s/\"/\%22/sgi;
     $a =~ s/\+/\%2B/sgi;
     $a =~ s/ /\+/sgi;
     return ($a)

}
