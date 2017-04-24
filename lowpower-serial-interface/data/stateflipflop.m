filename = 'stateflipflop.csv';
M = csvread(filename,1,0);
plot(M(:,1),M(:,2),M(:,1),M(:,4),M(:,1),M(:,6),M(:,1),M(:,8),M(:,1),M(:,10),M(:,1),M(:,12));
legend('reset in','clock in','D','Q','node 1', 'node 2');

