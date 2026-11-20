package booking;

import java.time.LocalDateTime;
import java.util.Optional;

public class ComputerClassRoom extends ClassRoom {

    private final int openingHour;
    private final int closingHour;

    public ComputerClassRoom(
            String name,
            String description,
            boolean hasProjector,
            int openingHour,
            int closingHour
    ) {
        super(name, description, hasProjector);
        this.openingHour = openingHour;
        this.closingHour = closingHour;
    }

    @Override
    public Optional<Booking> book(Interval interval, User user) {
        if (!withinOpeningHours(interval)) {
            return Optional.empty();
        }

        return super.book(interval, user);
    }

    private boolean withinOpeningHours(Interval interval) {
        LocalDateTime start = interval.getStart();
        LocalDateTime end = interval.getEnd();

        if (!start.toLocalDate().equals(end.toLocalDate())) {
            return false;
        }

        LocalDateTime opening = start.toLocalDate().atTime(openingHour, 0);
        LocalDateTime closing = start.toLocalDate().atTime(closingHour, 0);

        return !start.isBefore(opening) && !end.isAfter(closing);
    }
}