#!/usr/bin/perl

use strict;
use warnings;

open my $fh, '<', '/var/log/apache2/access.log' or die "Cannot open file: $!\n";

my %count;
my %first_visit;
my %last_visit;
while(<$fh>) {
    my $line = $_ if (($_ !~ /^192\.168/) && ($_ !~ /^\:\:1/));
    if ($line) {
	my @word= split / /, $line;
        my $ip = $word[0];
	my $time = $word[3];
        $time =~ s|\[||g;
	$count{$ip}++;
	$first_visit{$ip} = $time if !(exists $first_visit{$ip});
	$last_visit{$ip} = $time;
	# printf("%s @ %s\n", $ip, $time);
    }
}
foreach my $ip (sort keys %count) {
    if ($first_visit{$ip} ne $last_visit{$ip}) {
        printf "%-20s %-15s from [%s] to [%s] \n", $ip, $count{$ip}, $first_visit{$ip}, $last_visit{$ip};
    }
}
