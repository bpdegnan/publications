function runme()

load card1979data.mat

figure
%plot the extracted data
semilogy(card(1).vgs,card(1).current)
hold on;
semilogy(card(2).vgs,card(2).current,'g')
semilogy(card(3).vgs,card(3).current,'r')
semilogy(card(4).vgs,card(4).current,'c')
semilogy(card(5).vgs,card(5).current,'m')
semilogy(card(6).vgs,card(6).current,'y')
hold off

ch = get(gca,'children'); 
ln = ch(strmatch('line',get(ch,'Type')));
set(ln,'Linewidth',1);
title('Card et al. extracted drain current data')
xlabel('Vg');
ylabel('drain current (log)');
legend('125C','105C','65C','25C','-15C','-55C','Location','SouthEast');
axis([0.8 2.2 1e-12 1e-5])
%return;

% hold on;
% %figure
% semilogy(card(1).vgs,smooth(card(1).current),'g')
% 
% semilogy(card(2).vgs,smooth(card(2).current),'g')
% semilogy(card(3).vgs,smooth(card(3).current),'g')
% semilogy(card(4).vgs,smooth(card(4).current),'g')
% semilogy(card(5).vgs,smooth(card(5).current),'g')
% semilogy(card(6).vgs,smooth(card(6).current),'g')
% hold off
% 
% ch = get(gca,'children'); 
% ln = ch(strmatch('line',get(ch,'Type')));
% set(ln,'Linewidth',1);


%these are teh bounds for each entry from Card to extract the slope
% bounds_vglow(1)=1.3;bounds_vghigh(1)=1.5;  %eyeball approximate subvt range.
% bounds_vglow(2)=1.3;bounds_vghigh(2)=1.5;
% bounds_vglow(3)=1.3;bounds_vghigh(3)=1.6;
% bounds_vglow(4)=1.4;bounds_vghigh(4)=1.8;
% bounds_vglow(5)=1.5;bounds_vghigh(5)=1.9;
% bounds_vglow(6)=1.6;bounds_vghigh(6)=2.0;

bounds_vglow(1)=1.35;bounds_vghigh(1)=1.4;  %eyeball approximate subvt range.
bounds_vglow(2)=1.30;bounds_vghigh(2)=1.35;
%bounds_vglow(3)=1.25;bounds_vghigh(3)=1.4;
bounds_vglow(3)=1.3;bounds_vghigh(3)=1.5;
bounds_vglow(4)=1.5;bounds_vghigh(4)=1.55;
%bounds_vglow(4)=1.35;bounds_vghigh(4)=1.55;
bounds_vglow(5)=1.5;bounds_vghigh(5)=1.7;
bounds_vglow(6)=1.65;bounds_vghigh(6)=1.85;


for i=1:length(card)
%i=6;
   
    %because the data is extracted, you only can get close to the number.
   tmp=abs(bounds_vglow(i)-card(i).vgs);
   [index1 index1] = min(tmp);
   processing(i).index_lower=index1;
   processing(i).vg_lower=card(i).vgs(index1);
   processing(i).current_lower=card(i).current(index1);
   
   tmp=abs(bounds_vghigh(i)-card(i).vgs);
   [index1 index1] = min(tmp);
   processing(i).index_upper=index1;
   processing(i).vg_higher=card(i).vgs(index1);
   processing(i).current_higher=card(i).current(index1);
   %do the fit
   %card(i).vgs(processing(i).index_lower:processing(i).index_upper)
   tmp= polyfit(card(i).vgs(processing(i).index_lower:processing(i).index_upper), log(card(i).current(processing(i).index_lower:processing(i).index_upper)), 1);
   processing(i).slope=tmp(1);
   processing(i).intercept=tmp(2);
   %calculate the minimum current
   processing(i).current_min=min(card(i).current);
   
   
   
end

%now that we have the information from each of the lines for slope,
figure, semilogy(card(1).vgs,card(1).current)
hold on;
semilogy(card(2).vgs,card(2).current,'g')
semilogy(card(3).vgs,card(3).current,'r')
semilogy(card(4).vgs,card(4).current,'c')
semilogy(card(5).vgs,card(5).current,'m')
semilogy(card(6).vgs,card(6).current,'y')
hold off

ch = get(gca,'children'); 
ln = ch(strmatch('line',get(ch,'Type')));
set(ln,'Linewidth',1);
title('Current data with slope fit overlay')
xlabel('Vg');
ylabel('drain current (log)');
legend('125C','105C','65C','25C','-15C','-55C','Location','SouthEast');
axis([0.8 2.2 1e-12 1e-5])

%we can then plot them on top of the extracted data.
for i=1:length(card)
%i=6;
    tmp = 0;  %extension length of the fit from the upper and lower bounds.
    vg=card(i).vgs((processing(i).index_lower-tmp):(processing(i).index_upper+tmp));
    clear tmp;
    tmp(1)=processing(i).slope;
    tmp(2)=processing(i).intercept;
    cur  = exp(polyval(tmp, vg));
    hold on;
    plot(vg, cur,':k');
    plot(vg(1),cur(1),'xk');
    plot(vg(end),cur(end),'xk');
    hold off;
end

%if the fits look good, let's now calculate kappa.  We must assume that
%Vgs from card had the source at 0 (as they elude) for kappa Vg/Ut.
%first, create the "n" graph in the same way as Card.
figure
hold on
for i=1:length(card)
%i=6;
    tmp=card(i).temperature;
    plot(tmp,1/(calc_Ut(tmp)*(processing(i).slope)),'o');
end
hold off;

ch = get(gca,'children'); 
ln = ch(strmatch('line',get(ch,'Type')));
set(ln,'Linewidth',1);
axis([-80 160 2 4])
title(' "n" as described by Card et al. ');
ylabel('n');
xlabel('T (degrees C)');

%kappa plot
figure
hold on
for i=1:length(card)
%i=6;
    tmp=card(i).temperature;
    plot(tmp,((processing(i).slope)*calc_Ut(tmp)),'o');
    %plot(tmp,1/(1/(calc_Ut(tmp)*(processing(i).slope))),'o');
end
hold off;

ch = get(gca,'children'); 
ln = ch(strmatch('line',get(ch,'Type')));
set(ln,'Linewidth',1);
%axis([-80 160 2 4])
title('kappa as extracted from "n" data, (1/n)');
ylabel('kappa');
xlabel('T (degrees C)');

%now take the current leakage at 25C
%go and extract out the proportional change.

%leakage valves from which to make an trend
x_set(1)=card(1).temperature;
x_set(2)=card(2).temperature;
x_set(3)=card(3).temperature;
x_set(4)=card(4).temperature;
%x_set(5)=card(5).temperature;
%x_set(6)=card(6).temperature;
y_set(1)=processing(1).current_min;
y_set(2)=processing(2).current_min;
y_set(3)=processing(3).current_min;
y_set(4)=processing(4).current_min;
%y_set(5)=processing(5).current_min;
%y_set(6)=processing(6).current_min;

%extract the fit information
diodefit= polyfit(x_set,log(y_set),1);
%diodefit
fitx = [10:1:135];
fity  = exp(polyval(diodefit, fitx));

figure
semilogy(x_set,y_set,'o')
hold on;
semilogy(fitx,fity,'-g')
hold off;
title('Minimum measureable current')
xlabel('Temperature');
ylabel('drain current (log)');

%calculate the diode factor.
n_qual = 1.1/(2 *0.026 * diodefit(1) * 313)
str = sprintf('Slope of fit is %1.3d\ndiode quality factor is %1.3d',diodefit(1),n_qual);
legend(str,'Location','South')

ch = get(gca,'children'); 
ln = ch(strmatch('line',get(ch,'Type')));
set(ln,'Linewidth',1);


%subtract and calculate new slope valuves
for i=1:length(card)
   tmp= polyfit(x_set, log(y_set), 1);
   curoffset=exp(polyval(tmp, card(i).temperature));

%   if(i==1)
%     curoffset = 3.5180e-08;
% %     curoffset = 8.5180e-08;
%   elseif(i==2)
%     curoffset = 6.0560e-09;
% %    curoffset = 12.0560e-09;
%   end
   
   processing(i).current_floor=abs(card(i).current-curoffset);    
   tmp= polyfit(card(i).vgs(processing(i).index_lower:processing(i).index_upper), log(processing(i).current_floor(processing(i).index_lower:processing(i).index_upper)), 1);
   processing(i).new_slope=tmp(1);
   processing(i).new_intercept=tmp(2);
   
end
%graph the data with teh leakage subtracted out.
figure, semilogy(card(1).vgs,processing(1).current_floor,'b')
hold on;
semilogy(card(2).vgs,processing(2).current_floor,'g')
semilogy(card(3).vgs,processing(3).current_floor,'r')
semilogy(card(4).vgs,processing(4).current_floor,'c')
semilogy(card(5).vgs,processing(5).current_floor,'m')
semilogy(card(6).vgs,processing(6).current_floor,'y')
hold off
for i=1:length(card)
%i=6;
    tmp = 10;  %extension length of the fit from the upper and lower bounds.
    vg=card(i).vgs((processing(i).index_lower-tmp):(processing(i).index_upper+tmp));
    clear tmp;
    tmp(1)=processing(i).new_slope;
    tmp(2)=processing(i).new_intercept;
    cur  = exp(polyval(tmp, vg));
    hold on;
    plot(vg, cur,':k');
    plot(vg(1),cur(1),'xk');
    plot(vg(end),cur(end),'xk');
    hold off;
end

ch = get(gca,'children'); 
ln = ch(strmatch('line',get(ch,'Type')));
set(ln,'Linewidth',1);
title('Current data with offset removed.')
xlabel('Vg');
ylabel('drain current (log)');
legend('125C','105C','65C','25C','-15C','-55C','Location','SouthEast');
axis([0.8 2.2 1e-12 1e-5])
%new kappa plot
figure
hold on
for i=1:length(card)
%i=6;
    tmp=card(i).temperature;
    plot(tmp,((processing(i).slope)*calc_Ut(tmp)),'o');
    plot(tmp,((processing(i).new_slope)*calc_Ut(tmp)),'xr');
end
hold off;

ch = get(gca,'children'); 
ln = ch(strmatch('line',get(ch,'Type')));
set(ln,'Linewidth',1);
%axis([-80 160 2 4])
title('kappa over temperature');
ylabel('kappa');
xlabel('T (degrees C)');
legend('original data','offset subtracted','Location','SouthWest')









function result = calc_Ut(p_temperature)
%for the temperature in C, calculate the thermal voltage.
p_temperature = p_temperature + 273.15;
k=1.3806488E-23;
q=1.602176565E-19;

Ut = (k*p_temperature)/q;
result = Ut;
