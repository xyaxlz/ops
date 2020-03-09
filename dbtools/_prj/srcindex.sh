export PATH=.:/sbin:/usr/sbin:/usr/local/sbin:/usr/local/bin:/bin:/usr/bin:/usr/local/bin
SCI_PATH=`dirname $0`
CUR_PATH=$SCI_PATH

root=$CUR_PATH/../
tmp=$root/tmp/
cd $root
rm -rf _prj/cscope.*
[-d "$tmp"] || mkdir $root/tmp/
csfile=$root/tmp/cscope.files
touch $root/tmp/cscope.files
find $root/ -name "*.php" >  $csfile
find $root/ -name "*.html" >> $csfile
find $root/ -name "*.htm" >>  $csfile
find $root/ -name "*.sh" >>   $csfile
find $root/ -name "*.inc" >>  $csfile
find $root/ -name "*.sql" >>  $csfile
find $root/ -name "*.js" >>   $csfile
find $root/ -name "*.css" >>  $csfile
find $root/ -name "*.conf" >> $csfile
find $root/ -name "*.tpl" >>  $csfile
cd _prj
cscope -b  -i $csfile
