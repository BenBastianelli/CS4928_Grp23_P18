package booking;

import java.time.LocalDateTime;
import java.time.temporal.ChronoField;
import java.util.LinkedList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

public class ClassRoom implements Room {

    private final String name;
    private final String description;

    private final List<Booking> bookings = new LinkedList<>();

    private final boolean hasProjector;

    public ClassRoom(String name, String description, boolean hasProjector) {
        this.name = name;
        this.description = description;
        this.hasProjector = hasProjector;
    }

    public String getName() {
        return this.name;
    }

    public String getDescription() {
        return this.description;
    }

    public boolean hasProjector() {
        return this.hasProjector;
    }

    public List<Booking> getBookings() {
        return List.copyOf(this.bookings);
    }

    private boolean available(Interval i) {
        for (Booking b : this.getBookings()) {
            if (b.getInterval().overlapsWith(i)) {
                return false;
            }
        }

        return true;
    }

    /*
    Only allows bookings that start on the hour. (Floors second and microsecond values).
    Also makes sure that the booking is valid and that the room is available.
    */
    public Optional<Booking> book(Interval i, User u) {
        if (
            i.getStart().with(ChronoField.HOUR_OF_DAY, 0).isAfter(i.getEnd())
            || !available(i)
            || !startAndEndAtHour(i)
            || !startBeforeEnd(i)
        ) {
            return Optional.empty();
        }

        Booking b = new Booking(i, u);
        bookings.add(b);

        return Optional.of(b);
    }

    private static boolean startBeforeEnd(Interval i) {
        return !(i.getEnd().isBefore(i.getStart()) || i.getStart().isBefore(LocalDateTime.now()));
    }

    private static boolean startAndEndAtHour(Interval i) {
        LocalDateTime bst = i.getStart()
            .with(ChronoField.SECOND_OF_MINUTE, 0)
            .with(ChronoField.NANO_OF_SECOND, 0);

        LocalDateTime bed = i.getEnd()
            .with(ChronoField.SECOND_OF_MINUTE, 0)
            .with(ChronoField.NANO_OF_SECOND, 0);

        return !(bed.getMinute() != 0|| bed.with(ChronoField.HOUR_OF_DAY, 0).isAfter(bst));
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }

        if (o == null || this.getClass() != o.getClass()) {
            return false;
        }

        ClassRoom classRoom = (ClassRoom) o;
        return Objects.equals(this.getName(), classRoom.getName())
            && Objects.equals(this.hasProjector(), classRoom.hasProjector());
    }

    @Override
    public int hashCode() {
        return Objects.hash(this.getName(), this.hasProjector());
    }

    @Override
    public String toString() {
        return String.format(
                "Room %s \"%s\" #bookings: %s",
                this.getName(),
                this.getDescription(),
                this.getBookings().size()
        );
    }
}
