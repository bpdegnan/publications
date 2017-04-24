function runme
%this should plot the resulting data from the other
%runme_<set> data
short=runme_short;
min=runme_min;
square=runme_square;
long=runme_long;

for i_drain=1:3
    for i_temp=1:length(short)
        if(i_temp==1)
            figure
        end
        h_fet=short(i_temp).gatesweep(i_drain);
        if(h_fet.include==1)
            slope=h_fet.slope;
            temperature=h_fet.temperature;
            plot(temperature,slope,'ob')
        end
        if(i_temp==1)
            hold on
        end
        h_fet=min(i_temp).gatesweep(i_drain);
        if(h_fet.include==1)
            slope=h_fet.slope;
            temperature=h_fet.temperature;
            plot(temperature,slope,'sr')
        end
        h_fet=square(i_temp).gatesweep(i_drain);
        if(h_fet.include==1)
            slope=h_fet.slope;
            temperature=h_fet.temperature;
            plot(temperature,slope,'+c')
        end
        h_fet=long(i_temp).gatesweep(i_drain);
        if(h_fet.include==1)
            slope=h_fet.slope;
            temperature=h_fet.temperature;
            plot(temperature,slope,'dg')
        end 
        
        if(i_temp==length(short))
            str_title=sprintf('subthreshold slope factor for Vds of %1.1f for different nFET W/L ratios',h_fet.vdrain);
            title(str_title);
            str_xlabel=sprintf('temperature %cC', char(176));
            xlabel(str_xlabel);
            ylabel('kappa (subvt slope)');
            legend('2\mum x 300nm','2\mum x 350nm','2\mum x 2\mum','2\mum x 10\mum')
            axis([-60 80 0.6 0.8]);
            hold off;
        end        
    end
    
end

figure
hold on
j=1;
for i_drain=1:3
    for i_temp=1:length(short)
        h_fet=short(i_temp).gatesweep(i_drain);
        if(h_fet.include==1)
            slope=h_fet.slope;
            temperature=h_fet.temperature;
            if(i_drain==1)
                h(j)=plot(temperature,slope,'ob');
            elseif(i_drain==2)
                h(j)=plot(temperature,slope,'sr');
            else
                h(j)=plot(temperature,slope,'dg');
            end
            
        end 
        j=j+1;
    end
    
end
title('subthreshold slope factor 2\mum x 300nm nFET for different Vds');
str_xlabel=sprintf('temperature %cC', char(176));
xlabel(str_xlabel);
ylabel('kappa (subvt slope)');
legend([h(1) h(38) h(75)],{'3.3V Vds','1V Vds','100mV Vds'})
axis([-60 80 0.6 0.8]);
hold off;

figure
hold on
j=1;
for i_drain=1:3
    for i_temp=1:length(min)
        h_fet=min(i_temp).gatesweep(i_drain);
        if(h_fet.include==1)
            slope=h_fet.slope;
            temperature=h_fet.temperature;
            if(i_drain==1)
                h(j)=plot(temperature,slope,'ob');
            elseif(i_drain==2)
                h(j)=plot(temperature,slope,'sr');
            else
                h(j)=plot(temperature,slope,'dg');
            end
            
        end 
        j=j+1;
    end
    
end
title('subthreshold slope factor 2\mum x 350nm nFET for different Vds');
str_xlabel=sprintf('temperature %cC', char(176));
xlabel(str_xlabel);
ylabel('kappa (subvt slope)');
legend([h(1) h(38) h(75)],{'3.3V Vds','1V Vds','100mV Vds'})
axis([-60 80 0.6 0.8]);
hold off;

figure
hold on
j=1;
for i_drain=1:3
    for i_temp=1:length(square)
        h_fet=square(i_temp).gatesweep(i_drain);
        if(h_fet.include==1)
            slope=h_fet.slope;
            temperature=h_fet.temperature;
            if(i_drain==1)
                h(j)=plot(temperature,slope,'ob');
            elseif(i_drain==2)
                h(j)=plot(temperature,slope,'sr');
            else
                h(j)=plot(temperature,slope,'dg');
            end
            
        end 
        j=j+1;
    end
    
end
title('subthreshold slope factor 2\mum x 2\mum nFET for different Vds');
str_xlabel=sprintf('temperature %cC', char(176));
xlabel(str_xlabel);
ylabel('kappa (subvt slope)');
legend([h(1) h(38) h(75)],{'3.3V Vds','1V Vds','100mV Vds'})
axis([-60 80 0.6 0.8]);
hold off;


figure
hold on
j=1;
for i_drain=1:3
    for i_temp=1:length(long)
        h_fet=long(i_temp).gatesweep(i_drain);
        if(h_fet.include==1)
            slope=h_fet.slope;
            temperature=h_fet.temperature;
            if(i_drain==1)
                h(j)=plot(temperature,slope,'ob');
            elseif(i_drain==2)
                h(j)=plot(temperature,slope,'sr');
            else
                h(j)=plot(temperature,slope,'dg');
            end
            
        end 
        j=j+1;
    end
    
end
title('subthreshold slope factor 2\mum x 10\mum nFET for different Vds');
str_xlabel=sprintf('temperature %cC', char(176));
xlabel(str_xlabel);
ylabel('kappa (subvt slope)');
legend([h(1) h(38) h(75)],{'3.3V Vds','1V Vds','100mV Vds'})
axis([-60 80 0.6 0.8]);
hold off;


end