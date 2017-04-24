function result=runme_origionalplot()
load nfetdata.mat

%this requires alldata, and then just the nFET set

index = 2;% 
semilogy(nfet(index).square.sweep(1).gatesweep.vgate,smooth(smooth(-nfet(index).square.sweep(1).gatesweep.current)),'b');
hold on;
index = 7;% 
semilogy(nfet(index).square.sweep(1).gatesweep.vgate,smooth(smooth(-nfet(index).square.sweep(1).gatesweep.current)),'--g');
index = 8;
semilogy(nfet(index).square.sweep(1).gatesweep.vgate,smooth(smooth(-nfet(index).square.sweep(1).gatesweep.current)),'r');
index = 16;% 
semilogy(nfet(index).square.sweep(1).gatesweep.vgate,smooth(smooth(-nfet(index).square.sweep(1).gatesweep.current)),'--b');
index = 25;% 
semilogy(nfet(index).square.sweep(1).gatesweep.vgate,smooth(smooth(-nfet(index).square.sweep(1).gatesweep.current)),'g');
index = 27;% 
semilogy(nfet(index).square.sweep(1).gatesweep.vgate,smooth(smooth(-nfet(index).square.sweep(1).gatesweep.current)),'--r');
hold off;

axis([0.2 1.8 1e-11 1e-4]);
title('Drain current for increasing gate voltage for a nFET device over temperature.');
ylabel('I_D');
xlabel('V_g');

%now generate the slope graph
i_low=1e-9;
i_high=1e-8;
a_fetindex=[2 7 8 16 25 27];

for i_counter=1:length(a_fetindex)
    
    i_index=a_fetindex(i_counter);
    data_current=abs(-nfet(i_index).square.sweep(1).gatesweep.current);
    data_vgate=nfet(i_index).square.sweep(1).gatesweep.vgate;
    [~, marker_lowcurrent] = min(abs(data_current - i_low));
    [~, marker_highcurrent] = min(abs(data_current - i_high));
    fit_data = polyfit(data_vgate(marker_lowcurrent:marker_highcurrent), log(data_current(marker_lowcurrent:marker_highcurrent)),1);
    result.fitslope(i_counter)=fit_data(1);
    result.fitint(i_counter)=fit_data(2);
    result.temperature(i_counter)=nfet(i_index).square.tread;
    result.kappa(i_counter)=result.fitslope(i_counter)*calc_Ut(result.temperature(i_counter));
    result.n(i_counter)=1/result.kappa(i_counter);
    
end

a_temperature=[-80:80];
a_theory=result.kappa(1)./calc_Ut(a_temperature);
%plot(a_temperature,a_theory);

figure,plot(result.temperature,result.n,'ro');
title('Experimental change in slope of subthreshold region, n, over temperature');
xlabel('Temperature (C)');
ylabel('Slope of subthreshold region');
axis([-80 80 1.0 2.5])

% figure, plot(a_temperature,a_theory,result.temperature,result.fitslope,'ro');
% title('Experimental change in slope of subthreshold region over temperature');
% xlabel('Temperature (C)');
% ylabel('Slope of subthreshold region');
% axis([-80 80 20 45]);
% 
% 
end  %function end

function result = calc_Ut(p_temperature)
p_temperature = p_temperature + 273.15;
k=1.3806488E-23;
q=1.602176565E-19;

Ut = (k*p_temperature)/q;
result = Ut;

end






