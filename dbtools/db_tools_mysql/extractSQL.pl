#!/usr/bin/perl
# Name: extractSQL.pl 
# Author:  
# Version: 1.1
# Date: 2012-04-23 
# modify: 
#        show timestamp,repair bug insert on duplicate key show 2 queries

use Getopt::Long;
Getopt::Long::GetOptions(              
      'help'    => \$help,            
      'f=s'    => \$file,            
      'i=s'    => \$interface,            
      'p=i'    => \$port,           
      'c=i'    => \$count,           
      't:s' => \$sqltype); 

if ($file){
 $OUTPUT_FILE = "$file"; 
  if ( $help || ! $sqltype) {
    print "Usage 1: $0 <-i eth*> <-p 36**> [-t select|update|insert|replace] [-c count]\n";
    print "Usage 2: $0 <-f filename> < -t select|update|insert|replace >\n";
    exit;
   }
}else{
  if ( $help || ! $interface || ! $port) {
    print "Usage 1: $0 <-i eth*> <-p 36**> [-t select|update|insert|replace] [-c count]\n";
    print "Usage 2: $0 <-f filename(tcpdump)> (-t select|update|insert|replace)\n";
    exit;
  }

  if( ! $sqltype){
        $sqltype=select;
  }
  if( ! $count){
        $count=1000;
  }
  $OUTPUT_FILE    = "./tcpdump_outfile.txt"; 
  if ( -e $OUTPUT_FILE ){
	rename( $OUTPUT_FILE, $OUTPUT_FILE.".bak") || die("There is a file named $OUTPUT_FILE, can not rename to $OUTPUT_FILE.bak ");
  }
 #tcpdump -i eth0 dst port 3341 -nn -s 0 -A -X -c 10000 > test.log
 system("sudo tcpdump -i $interface dst port $port -nn -s 0 -A -X -c $count > $OUTPUT_FILE");
}


open(IN,$OUTPUT_FILE) || die "File not found.\n";
while ( $input = <IN> ){

        if ($input =~ /^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]/){

        	if(!@record){
                @ClientInfo = split(/ +/, $input);
		$time=$ClientInfo[0];
                $ClientIP=$ClientInfo[2];
                
            #print "sddss\n";
       	 next;
                }

        	if(@record){
                $sqlresult=join "",@record;
                if($sqlresult =~ s/\s//g){
                	$sqlresult=lc($sqlresult);
                	if($sqlresult =~ /$sqltype/){
                		$pos=index($sqlresult,"$sqltype");
						#print"$pos\n";
               			$leng=length($sqlresult);
                		$res=substr($sqlresult,$pos,$leng);
                		$res=~ s/`\.`/douhao/g ;
				$res=~ s/\./ /g;
				$res=~ s/douhao/`\.`/g;
                                $res=~ s/(.*from)\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)\s+([where|order|limit].*)/$1 $2\.$3 $4/gi;
                		#$ressort{$ClientIP}=$res;      		             		
                		printf("Time:%s ClientIP:%s-->SQL: %s\n",$time,$ClientIP,$res); 	
                	 }                	
                 }
                @ClientInfo = split(/ +/, $input);
		$time=$ClientInfo[0];
                $ClientIP=$ClientInfo[2];
                @record=[];
        next;
           }  #end if(@record)
        } #end if ($input =~ /^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]/)


        if ($input =~ /0x\d+/){

                @neirong=split(/ +/,$input);

                $a=pop(@neirong);

                chomp($a);

                @record=("@record","$a");

                chomp(@record);
        #print"@record\n";
        next;
        }

}#end while
