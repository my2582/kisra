 
-- 시계열 시가평가액	  
select B.ordered_date, sum(B.value) as value
  	    from (select to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') as ordered_date, value
                from detail
		       where userid='A002' order by ordered_date) B
	group by B.ordered_date
	



-- 시계열 수익률
select A.ordered_date as date, A.value, ln(A.value/lag(A.value) OVER (ORDER BY A.ordered_date)) as ret
from (select B.ordered_date, sum(B.value) as value
  	    from (select to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') as ordered_date, value
                from detail
		       where userid='A002' order by ordered_date) B
	   group by B.ordered_date) A
	   
	   

-- 누적수익률 및 연율 변동성
select exp(sum(R.ret))-1 as cum_ret, stddev(R.ret)*sqrt(250) as vol
  from (select A.ordered_date as date, ln(A.value/lag(A.value) OVER (ORDER BY A.ordered_date)) as ret
	      from (select B.ordered_date, sum(B.value) as value
			      from (select to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') as ordered_date, value
				          from detail
				         where userid='A002' order by ordered_date) B
  group by B.ordered_date) A) R