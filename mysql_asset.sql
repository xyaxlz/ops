CREATE TABLE `mysql_asset` (
	  `id` bigint(20) NOT NULL AUTO_INCREMENT,
	  `ip` varchar(36) COLLATE utf8_bin DEFAULT NULL,
	  `mip` varchar(36) COLLATE utf8_bin DEFAULT NULL,
	  `port` int(11) DEFAULT NULL,
	  `flag` tinyint(4) DEFAULT NULL,
	  `dbs` text COLLATE utf8_bin,
	  PRIMARY KEY (`id`),
	  UNIQUE KEY `uniq_ip_port` (`ip`,`port`)
) ENGINE=InnoDB AUTO_INCREMENT=2322 DEFAULT CHARSET=utf8 COLLATE=utf8_bin
