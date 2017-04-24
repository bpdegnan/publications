function runme_compare4007()

load card1979data.mat
load CD4007.mat


semilogy(gatesweep_single_CD4007.gatesweep(end).gatevoltage,smooth(gatesweep_single_CD4007.gatesweep(end).current),card(4).vgs,card(4).current,'c--');
axis([0.2 2.2 1e-12 1e-3])

end
