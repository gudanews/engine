#!/usr/bin/perl

use strict;
use warnings;

open FH1 , '<', '/var/log/apache2/access.log.1' or die "Cannot open file: $!\n";
my @data = <FH1>;
close FH1;
open FH, '<', '/var/log/apache2/access.log' or die "Cannot open file: $!\n";
push @data, <FH>;
close FH;
my %count;
my %first_visit;
my %last_visit;
foreach my $line (@data) {
    if (($line !~ /^192\.168/) && ($line !~ /^\:\:1/)) {
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
print "\nIPs with quick access:\n";
foreach my $ip (sort keys %count) {
    if (($first_visit{$ip} eq $last_visit{$ip}) || ($count{$ip} < 10)){
        printf "%-20s %-15s@[%s]\n", $ip, $count{$ip}, $last_visit{$ip};
    }
}
print "\nIPs with multiple access:\n";
foreach my $ip (sort keys %count) {
    if (($first_visit{$ip} ne $last_visit{$ip}) && ($count{$ip} >= 10)) {
        printf "%-20s %-15s from [%s] to [%s]\n", $ip, $count{$ip}, $first_visit{$ip}, $last_visit{$ip};
    }
}
