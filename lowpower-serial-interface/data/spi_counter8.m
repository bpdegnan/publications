filename = 'spi_counter8.csv';
M = csvread(filename,1,0);
%plot(M(:,1),M(:,2),M(:,1),M(:,6),M(:,1),M(:,8))
figure
title('Counter Block Signals');
subplot(3,1,1);
plot(M(:,1),M(:,2));
xlabel('Time');
ylabel('Clock');
subplot(3,1,2);
plot(M(:,1),M(:,6),'r');
xlabel('Time');
ylabel('Counter');
subplot(3,1,3);
plot(M(:,1),M(:,8),'g');
xlabel('Time');
ylabel('Latch');





