SELECT  p.page_title, r.rd_title 
FROM redirect as r
JOIN page as p
ON p.page_id = r.rd_from
where r.rd_title = "Asyut";

select count(*) from page;