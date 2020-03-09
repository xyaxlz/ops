#!/usr/bin/perl -w
use strict;
use Data::Dumper;
use POSIX qw(strftime);
use Digest::MD5;
use File::Find;
use LWP::UserAgent;
use Sys::Hostname;



#foreach my $logfile (@logfiles){
#	my $log = strftime($logfile,localtime(time()));
#	my @p = split('/',$log);
#	my $sg = $p[scalar(@p)-1];
#	$log =~ s/$sg//g;
#	find { preprocess => \&preprocess, wanted => sub{
#		my $name=$File::Find::name;
#		print $name if $name =~ /$sg/;
#	} },$log;
#	my @filelist = `find $log`;
#	print Dumper @filelist;
#}
#
#
#
#
#
#
#
#
#

#subhttp://shannon.pdtv.io:8360/msg/send







my $r;
my $c;
my $tmp_file = "/dev/shm/.logfile.tmp";
our $host = hostname;

open(TMPBUF,"$tmp_file") or die("$!");;
while(my $t = <TMPBUF>){
	chomp($t);
	next if $t =~ /^#/g;
	next if $t =~ /^\s/g;
	next if $t =~ /^$/g;
	my @tmp = split('\|',$t);
	next if scalar(@tmp)  < 2;
	next if $tmp[1] eq "";
	$c->{$tmp[1]}->{time}=$tmp[0];
	$c->{$tmp[1]}->{point}=$tmp[2];

}
close(TMPBUF);



sub SEDN_MGS
{
	#my ($who,$msg_array,$msg_array_line) = @_;
	my ($who,$msg_array,$caller,$msg_array_line) = @_;
	return 0 if scalar(@{$msg_array}) < 1;
print Dumper $msg_array;
	my $msg = "s4:".join(",",@{$msg_array});
	$msg =~ s/([^\w\-\.\@])/$1 eq "\n" ? "\n":sprintf("%%%2.2x",ord($1))/eg;
	my $msg_line = join(",",@{$msg_array_line}[0..2]);
	$msg_line =~ s/\s//gi;
	$msg_line =~ s/([^\w\-\.\@])/$1 eq "\n" ? "\n":sprintf("%%%2.2x",ord($1))/eg;
	#my $url = "http://shannon.pdtv.io:8360/msg/send?group_name=$who&subject=$msg&content=$msg_line-loginfo.pl-".$host;
	my $url = "http://shannon.pdtv.io:8360/msg/send?group_name=$who&subject=$msg&_caller=$caller&content=$msg_line-loginfo.pl-".$host;
	print $url;
	my $ua = LWP::UserAgent->new;
 	$ua->timeout(10);
 	my $response = $ua->get($url);
 	if ($response->is_success) {
		print $response->decoded_content;  # or whatever
	}else{
    		print "error:".$response->status_line;
 	}


}



while (<>){
	chomp();
	next if /^#/;
	next if /^\s/;
	my @conf = split('###');
	next if scalar(@conf) <= 0;
	my $log = strftime($conf[1],localtime(time()));
	my @find_logs = `find $log`;
	next if scalar(@find_logs) <= 0;
	foreach my $find_log (@find_logs){
		chomp($find_log);
		$r->{$conf[0]}->{$find_log}->{regular}=$conf[2];
		$r->{$conf[0]}->{$find_log}->{number}=$conf[3];
	}
}

sub p
{
	my $path = shift;
	return $1 if $path =~ /^\/data\/projlogs\/(.*?\/.*?)\//;
}

sub pcaller
{
	my $path = shift;
	return $1 if $path =~ /^\/data\/projlogs\/(.*?)\//;
}


while (my ($group,$next_index) = each %$r){
	#记录短信内容
	my @msg;
	#记录匹配为真的时候的行，用来发送邮件内容
	my @msg_array;
	my $caller="null";
	while(my ($logname,$index) = each %$next_index){
		my @tmp_array;
		if (-f $logname){
			my $start_point = 0;
			$start_point = $c->{$logname}->{point} if exists($c->{$logname}->{point});
			my $log_file_point = (stat($logname))[7];
			print "-- $start_point > $log_file_point";
			$start_point = 0 if ($start_point > $log_file_point);
			print " $logname==$start_point \n";
			########################################
			#qr/(\D+)(\d+)@(.*)/;
			my $rgx = qr/$index->{regular}/;

			########################################
			my $conn = 0;
			open(FILE_IN,"$logname") or die("$!");
			seek(FILE_IN,$start_point,0);
			while(my $line = <FILE_IN>){
				#$conn++ if $line=~ /$rgx/;
				#if ($conn > $index->{number}){
				#	push(@msg,$index->{regular}."出现超过".$index->{number}."次,在".&p($logname));
				#	last;
				#}
				if ($line=~ /$rgx/){
					$conn++;
					#if ($conn > $index->{number}){
					if ($conn >= $index->{number}){
                        			push(@msg,$index->{regular}."出现超过".$index->{number}."次,在".&p($logname));
						#push(@msg_array,@tmp_array);
						push(@msg_array,$line);
        					$caller=&pcaller($logname);
                                                last;
                                        }else{
						#push(@tmp_array,$line);
						push(@msg_array,$line);
					}
				}
			}
			close(FILE_IN);
			$c->{$logname}->{point} = $log_file_point;
			$c->{$logname}->{time}=time();
		}
        
	}
	###sendmail
	print Dumper @msg;
	#&SEDN_MGS($group,\@msg,\@msg_array);
	&SEDN_MGS($group,\@msg,$caller,\@msg_array);
}



##_save__$$

open(TMPWRITE,">$tmp_file") or die("$!");;
while (my ($a , $b) = each %$c){
	print TMPWRITE $b->{time}."|$a|".$b->{point}."\n";
}
close(TMPWRITE);

