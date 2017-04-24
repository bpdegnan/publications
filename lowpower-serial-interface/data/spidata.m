filename = 'spidata.csv';
M = csvread(filename,1,0);
plot(M(:,1),M(:,2),M(:,1),M(:,4),M(:,1),M(:,6),M(:,1),M(:,8))

figure
title('Counter Block Signals');
subplot(4,1,1);
plot(M(:,1),M(:,2)+1);
xlabel('Time');
ylabel('Reset');
subplot(4,1,2);
plot(M(:,1),M(:,4),'r');
xlabel('Time');
ylabel('Data');
subplot(4,1,3);
plot(M(:,1),M(:,6),'g');
xlabel('Time');
ylabel('Clock');
subplot(4,1,4);
plot(M(:,1),M(:,10),'k');
xlabel('Time');
ylabel('MUX Sel');

