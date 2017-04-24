filename = 'stateblock.csv';
M = csvread(filename,1,0);
plot(M(:,1),M(:,2),M(:,1),M(:,4),M(:,1),M(:,6),M(:,1),M(:,8),M(:,1),M(:,10),M(:,1),M(:,12),M(:,1),M(:,14),M(:,1),M(:,16));
legend('clk-in','state-in','state-out','match latch','match in', 'match out','chain in', 'chain out');


