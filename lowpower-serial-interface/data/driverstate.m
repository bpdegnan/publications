filename = 'driver-state.csv';
M = csvread(filename,1,0);
plot(M(:,1),M(:,2),M(:,1),M(:,4),M(:,1),M(:,6));

figure
title('Driver State Block Signals');
subplot(3,1,1);
plot(M(:,1),M(:,2));
xlabel('Time');
ylabel('Reset');
subplot(3,1,2);
plot(M(:,1),M(:,4),'r');
xlabel('Time');
ylabel('Data Valid');
subplot(3,1,3);
plot(M(:,1),M(:,6),'g');
xlabel('Time');
ylabel('State Out');


