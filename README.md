### 爬虫
建表：
```sql
-- 分类表
CREATE TABLE IF NOT EXISTS `classify` (
`id` varchar(255),
`pid` varchar(255),
`title` varchar(255),
`url` varchar(255),
`type` varchar(55),
PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- 商品信息表
CREATE TABLE IF NOT EXISTS `commodity` (
`id` varchar(255),
`cls_id` varchar(255),
`title` varchar(255),
`vendidos` varchar(50),
`month_vendidos` varchar(50),
`price_symbol` varchar(25),
`price` varchar(255),
`thumbnail` varchar(255),
`show_url` TEXT,
PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- 历史订单记录表
CREATE TABLE IF NOT EXISTS `history_order` (
`id` varchar(255),
`cid` varchar(255),
`country_name` varchar(255),
`country_code` varchar(255),
`name` varchar(255),
`quantity` varchar(255),
`unit` varchar(55),
PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
```

结果查询（_**mercado**_）：
```sql
SELECT DISTINCT
c.id AS "编号",
c.title AS '名称',
c.vendidos AS '销量',
c.month_vendidos AS '月销量',
concat( 'R$', c.price ) AS '参考价格',
c.show_url AS '详情链接'
FROM
commodity AS c,
classify AS s 
WHERE
c.cls_id = s.id 
AND s.type = 'mercado' 
ORDER BY
c.month_vendidos + 0 DESC 
LIMIT 1000;
```

根据历史销量查询（_**速卖通**_）~~待修改验证~~：
```sql
SELECT DISTINCT
c.cid AS 'ID',
c.NAME AS '名称',
c.vendidos AS '实时销量',
count( o.cid ) * o.quantity AS month_vendidos,
c.price AS '参考价格',
c.show_url AS '详情链接' 
FROM
commodity AS c,
history_order AS o,
classify AS s 
WHERE
c.cid = o.cid 
AND c.cls_id = s.cid 
AND s.type = 'ali' 
AND o.country_code = 'br' 
GROUP BY
c.cid 
ORDER BY
month_vendidos DESC 
LIMIT 1000
```