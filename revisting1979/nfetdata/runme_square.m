function result=runme_square
flag_plot=0;

load nfetdata.mat
a_vds=[1 2 3];
a_excludelist{1} = [24:29] ;  %this is the index exclude for bad data for set 1, etc
a_excludelist{2} = [24:29] ;
a_excludelist{3} = [24:29] ;

target_lower_subvt{1} = 1*10^-10;
target_upper_subvt{1} = 1*10^-7;
target_lower_subvt{2} = 1*10^-10;
target_upper_subvt{2} = 1*10^-7;
target_lower_subvt{3} = 1*10^-10;
target_upper_subvt{3} = 1*10^-7;


%plot the original data.
for i_counter_vds=1:length(a_vds);
    i_vds=a_vds(i_counter_vds);
    for i=1:length(nfet)
%         if(i==1)
%             figure
%         end
        h_fet=nfet(i).square.sweep(i_vds);
        h_fet_t=nfet(i).square.tread;
        [i_value,i_index]=min(abs(i-a_excludelist{i_vds}));
        result(i).gatesweep(i_vds).include=0;
        result(i).gatesweep(i_vds).vdrain=h_fet.gatesweep.vdrain;
        if(i_value~=0)
            result(i).gatesweep(i_vds).include=1;
            %result(i).gatesweep(i_vds).vdrain=h_fet.gatesweep.vdrain;
            result(i).gatesweep(i_vds).vgate=h_fet.gatesweep.vgate;
            result(i).gatesweep(i_vds).current=abs(h_fet.gatesweep.current);
            result(i).gatesweep(i_vds).temperature=h_fet_t;
         %   semilogy(h_fet.gatesweep.vgate,smooth(abs(h_fet.gatesweep.current)))
            %get the slope
            %current = smooth(abs(h_fet.gatesweep.current));
            current = smooth(smooth(smooth(abs(h_fet.gatesweep.current))));
            vgate = transpose(h_fet.gatesweep.vgate);
            for i_loop1=1:length(current)
                tmp_cur = current(i_loop1);
                if(tmp_cur < target_lower_subvt{i_vds})
                    offset_lower = i_loop1;
                end
            end

            for i_loop1=1:length(current)
                tmp_cur = current(i_loop1);
                if(tmp_cur < target_upper_subvt{i_vds})
                    offset_upper = i_loop1;
                end
            end
            fvg_subvt   = vgate(offset_lower:offset_upper);
            pc_subvt    = polyfit(fvg_subvt, log(current(offset_lower:offset_upper)), 1);
            result(i).gatesweep(i_vds).slope = pc_subvt(1)*calc_Ut(h_fet_t);
            %extract the threshold.
            extrapolate_current  = exp(polyval(pc_subvt,vgate));
             [~,i_startindex]=min(abs(target_upper_subvt{i_vds}-current));  %find the max point
             result(i).gatesweep(i_vds).vth=0;
             for i_trace=i_startindex:length(vgate);
                if((extrapolate_current(i_trace)/2) > current(i_trace))
                    result(i).gatesweep(i_vds).vth=current(i_trace);
                    break;
                end
             end
            
            
        end
%         if(i==1)
%             hold on
%         end
%         if(i==length(nfet))
%             hold off;
%         end
    end
end    


%now to plot the data
if(flag_plot)
hold on
for i_counter_vds=1:length(result(1).gatesweep)
   % i_counter_vds
%for i_counter_vds=1:1
    for i_counter_sweep=1:length(result)
        if(i_counter_sweep==1)
            figure
        end
        if(result(i_counter_sweep).gatesweep(i_counter_vds).include==1)
            temperature=result(i_counter_sweep).gatesweep(i_counter_vds).temperature;
            slope=result(i_counter_sweep).gatesweep(i_counter_vds).slope;
            str_note=sprintf('%i',i_counter_sweep);
            plot(temperature,slope,'o');
            text(temperature+1,slope,str_note);
        end
        if(i_counter_sweep==1)
            hold on
        end
        if(i_counter_sweep==length(result))
            %result(i_counter_sweep).gatesweep(i_counter_vds)
            str_title=sprintf('%1.2f',result(i_counter_sweep).gatesweep(i_counter_vds).vdrain);
            title(str_title);
            hold off;
        end
    end
end
hold off
end

end

function result = calc_Ut(p_temperature)
p_temperature = p_temperature + 273.15;
k=1.3806488E-23;
q=1.602176565E-19;

Ut = (k*p_temperature)/q;
result = Ut;

end