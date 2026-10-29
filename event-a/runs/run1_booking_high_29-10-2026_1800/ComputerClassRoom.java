package booking;

import java.time.LocalTime;
import java.util.Optional;

public class ComputerClassRoom extends ClassRoom {
    private final int openingHour;
    private final int closingHour;

    public ComputerClassRoom(
            String n, String d, boolean p, int openingHour, int closingHour) {
        super(n, d, p);

        if (openingHour < 0 || openingHour > 23
                || closingHour < 1 || closingHour > 23
                || openingHour >= closingHour) {
            throw new IllegalArgumentException("Invalid opening or closing hours");
        }

        this.openingHour = openingHour;
        this.closingHour = closingHour;
    }

    @Override
    public Optional<Booking> book(Interval i, User u) {
        LocalTime opening = LocalTime.of(this.openingHour, 0);
        LocalTime closing = LocalTime.of(this.closingHour, 0);

        if (i.getStart().toLocalTime().isBefore(opening)
                || i.getEnd().toLocalTime().isAfter(closing)) {
            return Optional.empty();
        }

        return super.book(i, u);
    }
}